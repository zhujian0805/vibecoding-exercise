"""
Gist service for GitHub API operations using Repository pattern
"""
import os
import logging
from typing import List, Optional
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
    
    def get_all_gists(self, user_id: int, max_gists: Optional[int] = None) -> List[Gist]:
        """Get all gists using GitHub library"""
        if max_gists is None:
            max_gists = int(os.environ.get('MAX_GISTS_FETCH', '1000'))
        
        try:
            # Get the authenticated user
            user = self.github_client.get_user()
            
            # Get gists using PyGithub
            github_gists = user.get_gists()
            
            gists = []
            count = 0
            
            logger.debug(f"Fetching up to {max_gists} gists using GitHub library")
            
            # Iterate through gists and convert to our Gist model
            for github_gist in github_gists:
                if count >= max_gists:
                    break
                    
                try:
                    # Convert GitHub gist object to our Gist model
                    gist = Gist.from_github_gist(github_gist)
                    gists.append(gist)
                    count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to convert gist {github_gist.id}: {e}")
                    continue
            
            logger.debug(f"Successfully fetched {len(gists)} gists")
            return gists
            
        except GithubException as e:
            logger.error(f"GitHub API error while fetching gists: {e}")
            raise
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
