    def test_gitrepo(self):
        """ Test the pygit2_utils.GitRepo() constructor
        """

        repo_path = os.path.join(self.gitroot, 'test_repo')

        self.assertRaises(
            OSError,
            pygit2_utils.GitRepo,
            repo_path,

        )

        # Fails: hash invalid
        self.assertRaises(
            ValueError,
            repo.diff,
            'foo'
        )
