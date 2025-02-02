"""
Git repository analysis module for collecting metrics and changes.
"""
from typing import Dict, List, Any
from pathlib import Path
import git
from loguru import logger


class GitMetricsCollector:
    """Collects and analyzes Git repository metrics."""
    
    def __init__(self, repo_path: str) -> None:
        """
        Initialize the collector with a repository path.
        
        Args:
            repo_path: Path to the Git repository
        """
        self.repo_path = Path(repo_path)
        try:
            self.repo = git.Repo(repo_path)
        except git.InvalidGitRepositoryError:
            logger.error(f"Invalid Git repository: {repo_path}")
            raise
            
    def analyze_commit(self, commit_hash: str) -> Dict[str, Any]:
        """
        Analyze a specific commit for various metrics.
        
        Args:
            commit_hash: The commit hash to analyze
            
        Returns:
            Dictionary containing commit metrics
        """
        commit = self.repo.commit(commit_hash)
        
        return {
            "hash": commit.hexsha,
            "author": commit.author.name,
            "timestamp": commit.authored_datetime.isoformat(),
            "message": commit.message.strip(),
            "files_changed": len(commit.stats.files),
            "insertions": commit.stats.total["insertions"],
            "deletions": commit.stats.total["deletions"],
            "total_changes": commit.stats.total["lines"],
            "files": self._get_file_changes(commit)
        }
    
    def _get_file_changes(self, commit: git.Commit) -> List[Dict[str, Any]]:
        """
        Get detailed file changes for a commit.
        
        Args:
            commit: Git commit object
            
        Returns:
            List of dictionaries containing file change details
        """
        changes = []
        for file_path, stats in commit.stats.files.items():
            changes.append({
                "path": file_path,
                "insertions": stats["insertions"],
                "deletions": stats["deletions"],
                "lines": stats["lines"],
                "type": self._get_file_type(file_path)
            })
        return changes
    
    def _get_file_type(self, file_path: str) -> str:
        """
        Determine the type of file based on extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            String indicating file type
        """
        ext = Path(file_path).suffix.lower()
        type_mapping = {
            ".py": "python",
            ".js": "javascript",
            ".java": "java",
            ".cpp": "cpp",
            ".h": "header",
            ".xml": "xml",
            ".json": "json",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".md": "markdown",
            ".txt": "text"
        }
        return type_mapping.get(ext, "other")
    
    def get_commit_history(self, 
                          max_count: int = 100, 
                          branch: str = "main") -> List[Dict[str, Any]]:
        """
        Get the commit history for analysis.
        
        Args:
            max_count: Maximum number of commits to retrieve
            branch: Branch to analyze
            
        Returns:
            List of commit analysis results
        """
        commits = []
        for commit in self.repo.iter_commits(branch, max_count=max_count):
            commits.append(self.analyze_commit(commit.hexsha))
        return commits
    
    def get_branch_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about branches in the repository.
        
        Returns:
            Dictionary containing branch metrics
        """
        branches = list(self.repo.heads)
        return {
            "total_branches": len(branches),
            "active_branches": [b.name for b in branches],
            "default_branch": self.repo.active_branch.name,
            "has_remote": bool(self.repo.remotes)
        }
