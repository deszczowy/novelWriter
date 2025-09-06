from git import Repo
import os
import datetime


class GitOperator:

    repository_path: str = None

    def get_path(self, file_path) -> None:
        r = None
        is_repo = False

        while not is_repo:
            try:
                try:
                    r = Repo(file_path)
                    is_repo = True
                except:
                    is_repo = False
                    current_path = os.path.dirname(file_path)
                    if file_path != current_path:
                        file_path = current_path
                    else:
                        break
            finally:
                r = None

        if is_repo:
            self.repository_path = file_path
        else:
            self.repository_path = None
    
    def commit(self) -> bool:
        repo = Repo(self.repository_path)

        if repo.is_dirty():
            index = repo.index

            # changed
            diffs = index.diff(None)
            for d in diffs:
                index.add([d.a_path])

            # new
            for u in repo.untracked_files:
                index.add([u])

            index.commit(self.session_description())
            return True

        return False
    
    def send_to_repo(self) -> bool:
        if self.commit():
            repo = Repo(self.repository_path)
            origin = repo.remotes.origin

            if origin.exists():
                origin.push()
    
    def fetch_data(self) -> None:
        repo = Repo(self.repository_path)
        if not repo.is_dirty():
            origin = repo.remotes.origin

            if origin.exists():
                origin.pull()
    
    def session_description(self) -> str:
        date_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return "{stamp}".format(stamp = date_stamp)


    def info(self) -> None:
        repo = Repo(self.repository_path)
        print(repo.remotes.origin)


class Repository:

    def pull(self, project_path: str) -> None:
        op = GitOperator()
        op.get_path(project_path)
        if op.repository_path is not None:
            op.fetch_data()
    
    def push(self, project_path: str) -> None:
        op = GitOperator()
        op.get_path(project_path)
        if op.repository_path is not None:
            op.send_to_repo()
