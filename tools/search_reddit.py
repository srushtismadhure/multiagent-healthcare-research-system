"""
search_reddit.py
Searches Reddit via PRAW for healthcare-relevant discussion.
Targets: r/healthIT, r/healthinformatics, r/datascience, r/MachineLearning, r/medicine
"""

import os
import praw
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


def get_reddit_client() -> praw.Reddit:
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "HealthResearcher/1.0"),
    )


def search_subreddit(
    subreddit: str,
    query: str,
    limit: int = 15,
    time_filter: str = "week",
) -> list[dict]:
    """
    Search a subreddit for posts matching a query.

    Returns list of:
        {
            "subreddit": str,
            "title": str,
            "score": int,
            "url": str,
            "permalink": str,
            "num_comments": int,
            "created_utc": str,
            "selftext_preview": str   # first 300 chars
        }
    """
    reddit = get_reddit_client()
    sub = reddit.subreddit(subreddit)

    results = []
    for post in sub.search(query, sort="relevance", time_filter=time_filter, limit=limit):
        results.append(
            {
                "subreddit": subreddit,
                "title": post.title,
                "score": post.score,
                "url": post.url,
                "permalink": f"https://reddit.com{post.permalink}",
                "num_comments": post.num_comments,
                "created_utc": datetime.utcfromtimestamp(post.created_utc).isoformat(),
                "selftext_preview": post.selftext[:300] if post.selftext else "",
            }
        )

    return results


def search_all_health_subreddits(query: str, limit: int = 10) -> list[dict]:
    """Search across all configured health subreddits."""
    subreddits = [
        "healthIT",
        "healthinformatics",
        "datascience",
        "MachineLearning",
        "medicine",
    ]
    all_results = []
    for sub in subreddits:
        try:
            all_results.extend(search_subreddit(sub, query, limit=limit))
        except Exception as e:
            print(f"[WARN] Failed to search r/{sub}: {e}")
    return all_results


if __name__ == "__main__":
    import sys
    import json

    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "AI healthcare clinical"
    results = search_all_health_subreddits(q)
    print(json.dumps(results, indent=2))
