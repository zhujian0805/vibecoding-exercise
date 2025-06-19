"""
Pull Request model to represent GitHub pull request data
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class PullRequestUser:
    """GitHub user model for pull request context"""
    login: str
    avatar_url: str
    html_url: str
    id: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            'login': self.login,
            'avatar_url': self.avatar_url,
            'html_url': self.html_url,
            'id': self.id
        }

    @classmethod
    def from_api_data(cls, user_data: dict):
        """Create PullRequestUser from GitHub API response data"""
        return cls(
            login=user_data.get('login', ''),
            avatar_url=user_data.get('avatar_url', ''),
            html_url=user_data.get('html_url', ''),
            id=user_data.get('id')
        )


@dataclass
class PullRequestRepository:
    """Repository information for pull request"""
    name: str
    full_name: str
    html_url: str
    id: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert repository to dictionary"""
        return {
            'name': self.name,
            'full_name': self.full_name,
            'html_url': self.html_url,
            'id': self.id
        }

    @classmethod
    def from_api_data(cls, repo_data: dict):
        """Create PullRequestRepository from GitHub API response data"""
        return cls(
            name=repo_data.get('name', ''),
            full_name=repo_data.get('full_name', ''),
            html_url=repo_data.get('html_url', ''),
            id=repo_data.get('id')
        )


@dataclass
class PullRequestBranch:
    """Branch information for pull request"""
    ref: str
    sha: str
    label: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert branch to dictionary"""
        return {
            'ref': self.ref,
            'sha': self.sha,
            'label': self.label
        }

    @classmethod
    def from_api_data(cls, branch_data: dict):
        """Create PullRequestBranch from GitHub API response data"""
        return cls(
            ref=branch_data.get('ref', ''),
            sha=branch_data.get('sha', ''),
            label=branch_data.get('label')
        )


@dataclass
class PullRequest:
    """GitHub pull request model"""
    id: int
    number: int
    title: str
    body: Optional[str] = None
    state: str = 'open'
    user: Optional[PullRequestUser] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    closed_at: Optional[str] = None
    merged_at: Optional[str] = None
    html_url: Optional[str] = None
    base: Optional[PullRequestBranch] = None
    head: Optional[PullRequestBranch] = None
    repository: Optional[PullRequestRepository] = None
    draft: bool = False
    mergeable: Optional[bool] = None
    mergeable_state: Optional[str] = None
    merged_by: Optional[PullRequestUser] = None
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0
    comments: int = 0
    review_comments: int = 0
    commits: int = 0
    assignees: Optional[List[PullRequestUser]] = None
    requested_reviewers: Optional[List[PullRequestUser]] = None
    labels: Optional[List[Dict[str, Any]]] = None

    def __post_init__(self):
        if self.assignees is None:
            self.assignees = []
        if self.requested_reviewers is None:
            self.requested_reviewers = []
        if self.labels is None:
            self.labels = []

    def to_dict(self) -> dict:
        """Convert pull request to dictionary"""
        return {
            'id': self.id,
            'number': self.number,
            'title': self.title,
            'body': self.body,
            'state': self.state,
            'user': self.user.to_dict() if self.user else None,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'closed_at': self.closed_at,
            'merged_at': self.merged_at,
            'html_url': self.html_url,
            'base': self.base.to_dict() if self.base else None,
            'head': self.head.to_dict() if self.head else None,
            'repository': self.repository.to_dict() if self.repository else None,
            'draft': self.draft,
            'mergeable': self.mergeable,
            'mergeable_state': self.mergeable_state,
            'merged_by': self.merged_by.to_dict() if self.merged_by else None,
            'additions': self.additions,
            'deletions': self.deletions,
            'changed_files': self.changed_files,
            'comments': self.comments,
            'review_comments': self.review_comments,
            'commits': self.commits,
            'assignees': [assignee.to_dict() for assignee in (self.assignees or [])],
            'requested_reviewers': [reviewer.to_dict() for reviewer in (self.requested_reviewers or [])],
            'labels': self.labels
        }

    @classmethod
    def from_github_pr(cls, github_pr, repository_info=None):
        """Create PullRequest from PyGithub pull request object"""
        try:
            # Extract user information
            user = None
            if hasattr(github_pr, 'user') and github_pr.user:
                user = PullRequestUser(
                    login=github_pr.user.login,
                    avatar_url=github_pr.user.avatar_url,
                    html_url=github_pr.user.html_url,
                    id=github_pr.user.id
                )

            # Extract base and head branch information
            base = None
            if hasattr(github_pr, 'base') and github_pr.base:
                base = PullRequestBranch(
                    ref=github_pr.base.ref,
                    sha=github_pr.base.sha,
                    label=github_pr.base.label
                )

            head = None
            if hasattr(github_pr, 'head') and github_pr.head:
                head = PullRequestBranch(
                    ref=github_pr.head.ref,
                    sha=github_pr.head.sha,
                    label=github_pr.head.label
                )

            # Extract repository information
            repo = None
            if repository_info:
                repo = PullRequestRepository.from_api_data(repository_info)
            elif hasattr(github_pr, 'base') and github_pr.base and hasattr(github_pr.base, 'repo'):
                repo_data = github_pr.base.repo
                repo = PullRequestRepository(
                    name=repo_data.name,
                    full_name=repo_data.full_name,
                    html_url=repo_data.html_url,
                    id=repo_data.id
                )

            # Extract merged_by information
            merged_by = None
            if hasattr(github_pr, 'merged_by') and github_pr.merged_by:
                merged_by = PullRequestUser(
                    login=github_pr.merged_by.login,
                    avatar_url=github_pr.merged_by.avatar_url,
                    html_url=github_pr.merged_by.html_url,
                    id=github_pr.merged_by.id
                )

            # Extract assignees
            assignees = []
            if hasattr(github_pr, 'assignees') and github_pr.assignees:
                for assignee in github_pr.assignees:
                    assignees.append(PullRequestUser(
                        login=assignee.login,
                        avatar_url=assignee.avatar_url,
                        html_url=assignee.html_url,
                        id=assignee.id
                    ))

            # Extract requested reviewers
            requested_reviewers = []
            if hasattr(github_pr, 'requested_reviewers') and github_pr.requested_reviewers:
                for reviewer in github_pr.requested_reviewers:
                    requested_reviewers.append(PullRequestUser(
                        login=reviewer.login,
                        avatar_url=reviewer.avatar_url,
                        html_url=reviewer.html_url,
                        id=reviewer.id
                    ))

            # Extract labels
            labels = []
            if hasattr(github_pr, 'labels') and github_pr.labels:
                for label in github_pr.labels:
                    labels.append({
                        'name': label.name,
                        'color': label.color,
                        'description': label.description
                    })

            return cls(
                id=github_pr.id,
                number=github_pr.number,
                title=github_pr.title,
                body=github_pr.body,
                state=github_pr.state,
                user=user,
                created_at=github_pr.created_at.isoformat() if github_pr.created_at else None,
                updated_at=github_pr.updated_at.isoformat() if github_pr.updated_at else None,
                closed_at=github_pr.closed_at.isoformat() if github_pr.closed_at else None,
                merged_at=github_pr.merged_at.isoformat() if github_pr.merged_at else None,
                html_url=github_pr.html_url,
                base=base,
                head=head,
                repository=repo,
                draft=getattr(github_pr, 'draft', False),
                mergeable=getattr(github_pr, 'mergeable', None),
                mergeable_state=getattr(github_pr, 'mergeable_state', None),
                merged_by=merged_by,
                additions=getattr(github_pr, 'additions', 0),
                deletions=getattr(github_pr, 'deletions', 0),
                changed_files=getattr(github_pr, 'changed_files', 0),
                comments=getattr(github_pr, 'comments', 0),
                review_comments=getattr(github_pr, 'review_comments', 0),
                commits=getattr(github_pr, 'commits', 0),
                assignees=assignees,
                requested_reviewers=requested_reviewers,
                labels=labels
            )

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create PullRequest from GitHub PR: {e}")
            # Return minimal pull request data
            return cls(
                id=getattr(github_pr, 'id', 0),
                number=getattr(github_pr, 'number', 0),
                title=getattr(github_pr, 'title', 'Unknown PR'),
                state=getattr(github_pr, 'state', 'unknown')
            )

    @classmethod
    def from_api_data(cls, pr_data: dict):
        """Create PullRequest from GitHub API response data"""
        try:
            # Extract user information
            user = None
            if pr_data.get('user'):
                user = PullRequestUser.from_api_data(pr_data['user'])

            # Extract base and head branch information
            base = None
            if pr_data.get('base'):
                base = PullRequestBranch.from_api_data(pr_data['base'])

            head = None
            if pr_data.get('head'):
                head = PullRequestBranch.from_api_data(pr_data['head'])

            # Extract repository information
            repo = None
            if pr_data.get('repository'):
                repo = PullRequestRepository.from_api_data(pr_data['repository'])
            elif pr_data.get('base', {}).get('repo'):
                repo = PullRequestRepository.from_api_data(pr_data['base']['repo'])

            # Extract merged_by information
            merged_by = None
            if pr_data.get('merged_by'):
                merged_by = PullRequestUser.from_api_data(pr_data['merged_by'])

            # Extract assignees
            assignees = []
            for assignee_data in pr_data.get('assignees', []):
                assignees.append(PullRequestUser.from_api_data(assignee_data))

            # Extract requested reviewers
            requested_reviewers = []
            for reviewer_data in pr_data.get('requested_reviewers', []):
                requested_reviewers.append(PullRequestUser.from_api_data(reviewer_data))

            return cls(
                id=pr_data.get('id', 0),
                number=pr_data.get('number', 0),
                title=pr_data.get('title', ''),
                body=pr_data.get('body'),
                state=pr_data.get('state', 'open'),
                user=user,
                created_at=pr_data.get('created_at'),
                updated_at=pr_data.get('updated_at'),
                closed_at=pr_data.get('closed_at'),
                merged_at=pr_data.get('merged_at'),
                html_url=pr_data.get('html_url'),
                base=base,
                head=head,
                repository=repo,
                draft=pr_data.get('draft', False),
                mergeable=pr_data.get('mergeable'),
                mergeable_state=pr_data.get('mergeable_state'),
                merged_by=merged_by,
                additions=pr_data.get('additions', 0),
                deletions=pr_data.get('deletions', 0),
                changed_files=pr_data.get('changed_files', 0),
                comments=pr_data.get('comments', 0),
                review_comments=pr_data.get('review_comments', 0),
                commits=pr_data.get('commits', 0),
                assignees=assignees,
                requested_reviewers=requested_reviewers,
                labels=pr_data.get('labels', [])
            )

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create PullRequest from API data: {e}")
            # Return minimal pull request data
            return cls(
                id=pr_data.get('id', 0),
                number=pr_data.get('number', 0),
                title=pr_data.get('title', 'Unknown PR'),
                state=pr_data.get('state', 'unknown')
            )
