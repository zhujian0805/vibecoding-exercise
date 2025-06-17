"""
Gist service for GitHub API operations using Repository pattern
"""
import os
import logging
import requests
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from github import Github, GithubException
from models.gist import Gist

logger = logging.getLogger(__name__)


class GistRepository:
    """Repository pattern for GitHub gist operations"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.github_client = Github(access_token)
    
    def get_total_gist_count(self) -> int:
        """Get total number of gists for the authenticated user"""
        try:
            user = self.github_client.get_user()
            gist_list = user.get_gists()
            return gist_list.totalCount
        except Exception as e:
            logger.warning(f"Failed to get total gist count: {e}")
            return 0
    
    def fetch_gists_page(self, page: int, per_page: int = 100) -> List[dict]:
        """Fetch a single page of gists using direct API call"""
        try:
            url = f"https://api.github.com/gists"
            headers = {
                'Authorization': f'token {self.access_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            params = {
                'per_page': per_page,
                'page': page
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to fetch gists page {page}: {e}")
            return []
    
    def get_all_gists(self, user_id: int, max_gists: Optional[int] = None) -> List[Gist]:
        """Get all gists with parallel page fetching"""
        if max_gists is None:
            max_gists = int(os.environ.get('MAX_GISTS_FETCH', '1000'))
        
        try:
            # Get total count and calculate pages needed
            total_gists = self.get_total_gist_count()
            actual_limit = min(total_gists, max_gists)
            
            # Return empty list if no gists to fetch
            if actual_limit == 0:
                logger.debug("No gists to fetch")
                return []
            
            per_page = 100  # GitHub's maximum per page
            num_pages = (actual_limit + per_page - 1) // per_page  # Ceiling division
            
            logger.debug(f"Fetching {actual_limit} gists across {num_pages} pages")
            
            # Fetch all pages in parallel
            all_gist_data = []
            max_workers = min(5, num_pages)  # Limit concurrent API calls
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_page = {
                    executor.submit(self.fetch_gists_page, page + 1, per_page): page + 1
                    for page in range(num_pages)
                }
                
                for future in as_completed(future_to_page):
                    page = future_to_page[future]
                    try:
                        page_data = future.result()
                        all_gist_data.extend(page_data)
                        logger.debug(f"Fetched page {page}: {len(page_data)} gists")
                    except Exception as e:
                        logger.error(f"Failed to fetch page {page}: {e}")
            
            logger.debug(f"Fetched {len(all_gist_data)} gists from {num_pages} pages")
            
            # Convert to Gist objects in parallel
            gists = []
            if all_gist_data:
                def convert_to_gist(gist_data):
                    try:
                        return Gist.from_api_data(gist_data)
                    except Exception as e:
                        logger.warning(f"Failed to convert gist {gist_data.get('id', 'unknown')}: {e}")
                        return None
                
                with ThreadPoolExecutor(max_workers=10) as executor:
                    future_to_gist = {
                        executor.submit(convert_to_gist, gist_data): gist_data
                        for gist_data in all_gist_data
                    }
                    
                    for future in as_completed(future_to_gist):
                        gist = future.result()
                        if gist:
                            gists.append(gist)
            
            logger.debug(f"Successfully processed {len(gists)} gists")
            return gists
            
        except Exception as e:
            logger.error(f"Failed to fetch gists: {e}")
            raise


class GistService:
    """Service for gist operations with business logic"""
    
    def __init__(self, repository: GistRepository):
        self.repository = repository
    
    def get_all_gists(self, user_id: int) -> List[Gist]:
        """Get all gists for a user"""
        return self.repository.get_all_gists(user_id)
    
    def filter_gists(self, gists: List[Gist], search_query: Optional[str] = None) -> List[Gist]:
        """Filter gists based on search query"""
        if not search_query or not search_query.strip():
            return gists
        
        search_query = search_query.strip().lower()
        filtered_gists = []
        
        for gist in gists:
            # Search in description and filenames
            if (gist.description and search_query in gist.description.lower()) or \
               any(search_query in file.filename.lower() for file in (gist.files or [])) or \
               any(file.language and search_query in file.language.lower() for file in (gist.files or [])):
                filtered_gists.append(gist)
        
        return filtered_gists
    
    def sort_gists(self, gists: List[Gist], sort: str = 'updated', 
                   table_sort: Optional[str] = None, table_sort_direction: str = 'asc') -> List[Gist]:
        """Sort gists with various criteria"""
        
        # Table sorting takes precedence over regular sorting
        if table_sort:
            sort_key = table_sort
            reverse = table_sort_direction == 'desc'
        else:
            sort_key = sort
            reverse = True  # Default to descending for most sorts
        
        try:
            if sort_key == 'description':
                gists.sort(key=lambda g: (g.description or '').lower(), reverse=reverse)
            elif sort_key == 'comments':
                gists.sort(key=lambda g: g.comments, reverse=reverse)
            elif sort_key == 'files':
                gists.sort(key=lambda g: len(g.files or []), reverse=reverse)
            elif sort_key == 'public':
                gists.sort(key=lambda g: g.public, reverse=reverse)
            elif sort_key == 'created_at' or sort_key == 'created':
                gists.sort(key=lambda g: g.created_at or '', reverse=reverse)
            elif sort_key == 'updated_at' or sort_key == 'updated':
                gists.sort(key=lambda g: g.updated_at or '', reverse=reverse)
            else:
                # Default to updated_at descending
                gists.sort(key=lambda g: g.updated_at or '', reverse=True)
                
        except Exception as e:
            logger.warning(f"Failed to sort gists by {sort_key}: {e}")
            # Fallback to description sorting
            gists.sort(key=lambda g: (g.description or '').lower())
        
        return gists
    
    def paginate_gists(self, gists: List[Gist], page: int = 1, 
                       per_page: int = 30) -> tuple[List[Gist], dict]:
        """Paginate gists and return pagination info"""
        per_page = min(per_page, 100)  # Limit max per page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_gists = gists[start_idx:end_idx]
        
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total_count': len(gists),
            'total_pages': (len(gists) + per_page - 1) // per_page if len(gists) > 0 else 1,
            'has_next': end_idx < len(gists),
            'has_prev': page > 1
        }
        
        return paginated_gists, pagination_info
