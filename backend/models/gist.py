"""
Gist model to represent GitHub gist data
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class GistFile:
    """GitHub gist file model"""
    filename: str
    type: str
    language: Optional[str] = None
    raw_url: Optional[str] = None
    size: int = 0
    truncated: bool = False
    content: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert gist file to dictionary"""
        return {
            'filename': self.filename,
            'type': self.type,
            'language': self.language,
            'raw_url': self.raw_url,
            'size': self.size,
            'truncated': self.truncated,
            'content': self.content
        }

    @classmethod
    def from_api_data(cls, filename: str, file_data: dict):
        """Create GistFile from GitHub API response data"""
        return cls(
            filename=filename,
            type=file_data.get('type', ''),
            language=file_data.get('language'),
            raw_url=file_data.get('raw_url'),
            size=file_data.get('size', 0),
            truncated=file_data.get('truncated', False),
            content=file_data.get('content')
        )


@dataclass
class Gist:
    """GitHub gist model"""
    id: str
    description: Optional[str] = None
    public: bool = True
    html_url: Optional[str] = None
    git_pull_url: Optional[str] = None
    git_push_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    comments: int = 0
    files: Optional[List[GistFile]] = None
    owner_login: Optional[str] = None
    owner_avatar_url: Optional[str] = None
    truncated: bool = False

    def __post_init__(self):
        if self.files is None:
            self.files = []

    def to_dict(self) -> dict:
        """Convert gist to dictionary"""
        files_list = self.files or []
        return {
            'id': self.id,
            'description': self.description,
            'public': self.public,
            'html_url': self.html_url,
            'git_pull_url': self.git_pull_url,
            'git_push_url': self.git_push_url,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'comments': self.comments,
            'files': [file.to_dict() for file in files_list],
            'owner': {
                'login': self.owner_login,
                'avatar_url': self.owner_avatar_url
            },
            'truncated': self.truncated,
            'file_count': len(files_list)
        }

    @classmethod
    def from_github_gist(cls, github_gist):
        """Create Gist from PyGithub gist object"""
        try:
            files = []
            for filename, file_data in github_gist.files.items():
                gist_file = GistFile(
                    filename=filename,
                    type=getattr(file_data, 'type', ''),
                    language=getattr(file_data, 'language', None),
                    raw_url=getattr(file_data, 'raw_url', None),
                    size=getattr(file_data, 'size', 0),
                    truncated=getattr(file_data, 'truncated', False),
                    content=getattr(file_data, 'content', None)
                )
                files.append(gist_file)

            return cls(
                id=github_gist.id,
                description=github_gist.description,
                public=github_gist.public,
                html_url=github_gist.html_url,
                git_pull_url=github_gist.git_pull_url,
                git_push_url=github_gist.git_push_url,
                created_at=github_gist.created_at.isoformat() if github_gist.created_at else None,
                updated_at=github_gist.updated_at.isoformat() if github_gist.updated_at else None,
                comments=github_gist.comments,
                files=files,
                owner_login=github_gist.owner.login if github_gist.owner else None,
                owner_avatar_url=github_gist.owner.avatar_url if github_gist.owner else None,
                truncated=getattr(github_gist, 'truncated', False)
            )
        except Exception as e:
            raise ValueError(f"Error creating Gist from GitHub gist: {e}")

    @classmethod
    def from_api_data(cls, gist_data: dict):
        """Create Gist from GitHub API response data"""
        try:
            files = []
            files_data = gist_data.get('files', {})
            for filename, file_data in files_data.items():
                gist_file = GistFile.from_api_data(filename, file_data)
                files.append(gist_file)

            owner = gist_data.get('owner', {})
            
            return cls(
                id=gist_data.get('id', ''),
                description=gist_data.get('description'),
                public=gist_data.get('public', True),
                html_url=gist_data.get('html_url'),
                git_pull_url=gist_data.get('git_pull_url'),
                git_push_url=gist_data.get('git_push_url'),
                created_at=gist_data.get('created_at'),
                updated_at=gist_data.get('updated_at'),
                comments=gist_data.get('comments', 0),
                files=files,
                owner_login=owner.get('login'),
                owner_avatar_url=owner.get('avatar_url'),
                truncated=gist_data.get('truncated', False)
            )
        except Exception as e:
            raise ValueError(f"Error creating Gist from API data: {e}")
