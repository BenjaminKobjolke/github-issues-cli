"""Every literal that is used in more than one place. No logic lives here."""

DATE_FORMAT = "%Y-%m-%d"  # shared by the frontmatter dates and the comment headings
MARKDOWN_SUFFIX = ".md"
FILE_ENCODING = "utf-8"

ISSUE_NUMBER_WIDTH = 5  # zero-padding, so the folder sorts by issue number
SLUG_UNSAFE_CHARS = r"[^a-z0-9]+"
SLUG_MAX_LEN = 50
SLUG_FALLBACK = "issue"
REPO_DIR_SEPARATOR = "__"  # "owner/repo" -> "owner__repo", one folder level
GHOST_AUTHOR = "ghost"  # what GitHub shows for a deleted account

GH_EXECUTABLE = "gh"
GH_ISSUE_FIELDS = "number,title,body,author,labels,state,createdAt,updatedAt,url"
GH_COMMENT_FIELDS = "comments"
GH_SORT_SEARCH = "sort:created-asc"

GITHUB_HOSTS = ("github.com", "www.github.com")
REPO_SLUG_PATTERN = r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$"
GIT_SUFFIX = ".git"

STATE_OPEN = "open"
STATE_CHOICES = (STATE_OPEN, "closed", "all")

DEFAULT_OUT_DIR = "./issues"
DEFAULT_STATE = STATE_OPEN
DEFAULT_LIMIT = 5000

LOGGING_ERROR = "error"
LOGGING_VERBOSE = "verbose"

EXIT_OK = 0
EXIT_GH_FAILED = 1
EXIT_BAD_INPUT = 2
