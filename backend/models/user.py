"""
User model to represent GitHub user data
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """GitHub user model"""
    login: str
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    company: Optional[str] = None
    blog: Optional[str] = None
    twitter_username: Optional[str] = None
    public_repos: int = 0
    total_repos: int = 0
    total_gists: int = 0
    followers: int = 0
    following: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    html_url: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            'login': self.login,
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'location': self.location,
            'company': self.company,
            'blog': self.blog,
            'twitter_username': self.twitter_username,
            'public_repos': self.public_repos,
            'total_repos': self.total_repos,
            'total_gists': self.total_gists,
            'followers': self.followers,
            'following': self.following,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'html_url': self.html_url
        }

    @classmethod
    def from_github_user(cls, github_user, total_repos: Optional[int] = None, total_gists: Optional[int] = None):
        """Create User from PyGithub user object"""
        return cls(
            login=github_user.login,
            id=github_user.id,
            name=github_user.name,
            email=github_user.email,
            avatar_url=github_user.avatar_url,
            bio=github_user.bio,
            location=github_user.location,
            company=github_user.company,
            blog=github_user.blog,
            twitter_username=getattr(github_user, 'twitter_username', None),
            public_repos=github_user.public_repos,
            total_repos=total_repos or github_user.public_repos,
            total_gists=total_gists or 0,
            followers=github_user.followers,
            following=github_user.following,
            created_at=github_user.created_at.isoformat() if github_user.created_at else None,
            updated_at=github_user.updated_at.isoformat() if github_user.updated_at else None,
            html_url=github_user.html_url
        )
