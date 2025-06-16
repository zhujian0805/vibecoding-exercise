"""
Repository model to represent GitHub repository data
"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Repository:
    """GitHub repository model"""
    id: int
    name: str
    full_name: str
    description: Optional[str] = None
    private: bool = False
    html_url: Optional[str] = None
    clone_url: Optional[str] = None
    ssh_url: Optional[str] = None
    language: Optional[str] = None
    stargazers_count: int = 0
    watchers_count: int = 0
    forks_count: int = 0
    size: int = 0
    default_branch: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    pushed_at: Optional[str] = None
    archived: bool = False
    disabled: bool = False
    fork: bool = False
    topics: List[str] = None
    visibility: str = "public"
    owner_login: Optional[str] = None
    owner_type: Optional[str] = None

    def __post_init__(self):
        if self.topics is None:
            self.topics = []

    def to_dict(self) -> dict:
        """Convert repository to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'full_name': self.full_name,
            'description': self.description,
            'private': self.private,
            'html_url': self.html_url,
            'clone_url': self.clone_url,
            'ssh_url': self.ssh_url,
            'language': self.language,
            'stargazers_count': self.stargazers_count,
            'watchers_count': self.watchers_count,
            'forks_count': self.forks_count,
            'size': self.size,
            'default_branch': self.default_branch,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'pushed_at': self.pushed_at,
            'archived': self.archived,
            'disabled': self.disabled,
            'fork': self.fork,
            'topics': self.topics,
            'visibility': self.visibility,
            'owner': {
                'login': self.owner_login,
                'type': self.owner_type
            }
        }

    @classmethod
    def from_github_repo(cls, github_repo):
        """Create Repository from PyGithub repository object"""
        try:
            topics = []
            try:
                if hasattr(github_repo, 'get_topics'):
                    topics = list(github_repo.get_topics())
            except Exception:
                topics = []

            return cls(
                id=github_repo.id,
                name=github_repo.name,
                full_name=github_repo.full_name,
                description=github_repo.description,
                private=github_repo.private,
                html_url=github_repo.html_url,
                clone_url=github_repo.clone_url,
                ssh_url=github_repo.ssh_url,
                language=github_repo.language,
                stargazers_count=github_repo.stargazers_count,
                watchers_count=github_repo.watchers_count,
                forks_count=github_repo.forks_count,
                size=github_repo.size,
                default_branch=github_repo.default_branch,
                created_at=github_repo.created_at.isoformat() if github_repo.created_at else None,
                updated_at=github_repo.updated_at.isoformat() if github_repo.updated_at else None,
                pushed_at=github_repo.pushed_at.isoformat() if github_repo.pushed_at else None,
                archived=github_repo.archived,
                disabled=github_repo.disabled,
                fork=github_repo.fork,
                topics=topics,
                visibility='private' if github_repo.private else 'public',
                owner_login=github_repo.owner.login,
                owner_type=github_repo.owner.type
            )
        except Exception as e:
            raise ValueError(f"Error creating Repository from GitHub repo: {e}")

    @classmethod
    def from_api_data(cls, repo_data: dict):
        """Create Repository from GitHub API response data"""
        try:
            topics = repo_data.get('topics', [])
            owner = repo_data.get('owner', {})
            
            return cls(
                id=repo_data.get('id'),
                name=repo_data.get('name'),
                full_name=repo_data.get('full_name'),
                description=repo_data.get('description'),
                private=repo_data.get('private', False),
                html_url=repo_data.get('html_url'),
                clone_url=repo_data.get('clone_url'),
                ssh_url=repo_data.get('ssh_url'),
                language=repo_data.get('language'),
                stargazers_count=repo_data.get('stargazers_count', 0),
                watchers_count=repo_data.get('watchers_count', 0),
                forks_count=repo_data.get('forks_count', 0),
                size=repo_data.get('size', 0),
                default_branch=repo_data.get('default_branch'),
                created_at=repo_data.get('created_at'),
                updated_at=repo_data.get('updated_at'),
                pushed_at=repo_data.get('pushed_at'),
                archived=repo_data.get('archived', False),
                disabled=repo_data.get('disabled', False),
                fork=repo_data.get('fork', False),
                topics=topics,
                visibility=repo_data.get('visibility', 'private' if repo_data.get('private') else 'public'),
                owner_login=owner.get('login'),
                owner_type=owner.get('type')
            )
        except Exception as e:
            raise ValueError(f"Error creating Repository from API data: {e}")
