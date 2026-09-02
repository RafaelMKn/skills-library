#!/usr/bin/env python3
"""
Skill Finder - Search and manage Agent Skills.

Features:
- Local index search (fast, offline)
- GitHub Code Search API fallback
- Web search URLs as final fallback
- Add new sources (--add-source)
- Update index from sources (--update)
- Show skill details (--info)
- Install skills locally (--install)
- Star favorite skills (--star)
- Similar skill recommendations
- Statistics (--stats)
- Tag search (#azure #bicep)

Author: yamapan (https://github.com/aktsmm)
License: MIT
"""

import argparse
import json
import re
import subprocess
import sys
import urllib.parse
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

# Windows consoles default to cp1252, which can't encode the emoji used below.
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Paths
SCRIPT_DIR = Path(__file__).parent
INDEX_PATH = SCRIPT_DIR / ".." / "references" / "skill-index.json"
STARS_PATH = SCRIPT_DIR / ".." / "references" / "starred-skills.json"
INSTALL_DIR = Path.home() / ".skills"  # Default install directory

# Configuration
AUTO_UPDATE_DAYS = 7  # Auto-update if index is older than this


# =============================================================================
# Index Management
# =============================================================================

def load_index() -> Optional[Dict[str, Any]]:
    """Load skill index from JSON file."""
    if not INDEX_PATH.exists():
        print(f"⚠️ Index file not found: {INDEX_PATH}")
        return None
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_index(index: Dict[str, Any]) -> None:
    """Save skill index to JSON file."""
    index["lastUpdated"] = date.today().isoformat()
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"✅ Index saved: {INDEX_PATH}")


def is_index_outdated(index: Dict[str, Any]) -> bool:
    """Check if index is older than AUTO_UPDATE_DAYS."""
    last_updated = index.get("lastUpdated", "")
    if not last_updated:
        return True
    try:
        last_date = datetime.fromisoformat(last_updated)
        age = datetime.now() - last_date
        return age > timedelta(days=AUTO_UPDATE_DAYS)
    except ValueError:
        return True


def check_and_auto_update(index: Dict[str, Any], silent: bool = False) -> Dict[str, Any]:
    """Check if index needs update and prompt user."""
    if is_index_outdated(index):
        last_updated = index.get("lastUpdated", "unknown")
        if not silent:
            print(f"\n⚠️ Index is outdated (last updated: {last_updated})")
            try:
                answer = input("🔄 Update now? [Y/n]: ").strip().lower()
                if answer in ["", "y", "yes"]:
                    update_all_sources()
                    # Reload index
                    return load_index() or index
            except (EOFError, KeyboardInterrupt):
                print("\n  Skipped")
    return index


def load_stars() -> List[str]:
    """Load starred skills list."""
    if not STARS_PATH.exists():
        return []
    with open(STARS_PATH, "r", encoding="utf-8") as f:
        return json.load(f).get("starred", [])


def save_stars(starred: List[str]) -> None:
    """Save starred skills list."""
    STARS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STARS_PATH, "w", encoding="utf-8") as f:
        json.dump({"starred": starred, "lastUpdated": date.today().isoformat()}, f, indent=2)


# =============================================================================
# Search Functions
# =============================================================================

def search_local(index: Dict, query: str = "", category: str = "", source: str = "", 
                 tags: List[str] = None) -> List[Dict]:
    """Search skills in local index with optional tag support."""
    results = index.get("skills", [])
    
    # Keyword filter (supports #tag syntax)
    if query:
        # Extract tags from query
        tag_pattern = r'#(\w+)'
        extracted_tags = re.findall(tag_pattern, query)
        clean_query = re.sub(tag_pattern, '', query).strip().lower()
        
        if extracted_tags:
            tags = (tags or []) + extracted_tags
        
        if clean_query:
            results = [s for s in results 
                      if clean_query in s["name"].lower() 
                      or clean_query in s.get("description", "").lower()]
    
    # Tag filter (matches categories)
    if tags:
        results = [s for s in results 
                  if any(tag.lower() in [c.lower() for c in s.get("categories", [])] 
                        for tag in tags)]
    
    # Category filter
    if category:
        results = [s for s in results if category in s.get("categories", [])]
    
    # Source filter
    if source:
        results = [s for s in results if s.get("source") == source]
    
    # Add source info and star status
    sources = {s["id"]: s for s in index.get("sources", [])}
    starred = load_stars()
    for skill in results:
        src = sources.get(skill.get("source"), {})
        skill["sourceUrl"] = src.get("url", "")
        skill["sourceName"] = src.get("name", skill.get("source", ""))
        skill["starred"] = f"{skill['source']}/{skill['name']}" in starred
    
    # Sort: starred first
    results.sort(key=lambda x: (not x.get("starred", False), x["name"]))
    
    return results


def search_github(query: str) -> List[Dict]:
    """Search skills on GitHub using gh CLI."""
    print("\n🌐 Searching GitHub...")
    
    search_query = f"{query} filename:SKILL.md" if query else "filename:SKILL.md path:.github/skills"
    
    try:
        result = subprocess.run(
            ["gh", "search", "code", search_query, "--json", "repository,path,url", "--limit", "15"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except FileNotFoundError:
        print("  ⚠️ GitHub CLI (gh) not found. Install it for external search.")
    except subprocess.TimeoutExpired:
        print("  ⚠️ GitHub search timed out.")
    except json.JSONDecodeError:
        print("  ⚠️ Invalid response from GitHub.")
    
    return []


def show_web_search_urls(query: str) -> None:
    """Show web search URLs for manual search."""
    terms = f"claude skill {query} OR copilot skill {query} SKILL.md" if query else "claude skills SKILL.md github"
    encoded = urllib.parse.quote(terms)
    
    print("\n🔎 Web Search URLs:")
    print(f"  Google: https://www.google.com/search?q={encoded}")
    print(f"  Bing: https://www.bing.com/search?q={encoded}")
    print(f"  DuckDuckGo: https://duckduckgo.com/?q={encoded}")


# =============================================================================
# Source Management
# =============================================================================

def add_source(repo_url: str) -> None:
    """Add a new source repository to the index."""
    index = load_index()
    if not index:
        return
    
    # Parse GitHub URL
    match = re.search(r"github\.com[/:]([^/]+)/([^/]+)", repo_url)
    if not match:
        print(f"❌ Invalid GitHub URL: {repo_url}")
        return
    
    owner, repo = match.groups()
    repo = repo.rstrip(".git")
    repo_full = f"{owner}/{repo}"
    
    # Check if already exists
    for src in index.get("sources", []):
        if repo_full in src.get("url", ""):
            print(f"⚠️ Source already exists: {src['id']}")
            # Still try to update skills
            update_source_skills(index, src["id"], repo_full)
            return
    
    # Create source ID
    source_id = re.sub(r'[^a-z0-9-]', '-', repo.lower())
    
    # Add source
    new_source = {
        "id": source_id,
        "name": repo,
        "url": f"https://github.com/{repo_full}",
        "type": "community",
        "description": f"Skills from {repo_full}"
    }
    index["sources"].append(new_source)
    save_index(index)
    
    print(f"\n📦 Added new source:")
    print(f"  ID: {source_id}")
    print(f"  URL: https://github.com/{repo_full}")
    
    # Fetch skills
    update_source_skills(index, source_id, repo_full)


def update_source_skills(index: Dict, source_id: str, repo_full: str) -> None:
    """Fetch and update skills from a source repository using GitHub Code Search API."""
    print("\n🔍 Searching for skills...")
    found_skills = []
    
    # Method 1: Use GitHub Code Search API to find all SKILL.md files
    try:
        result = subprocess.run(
            ["gh", "api", "search/code", "-f", f"q=repo:{repo_full} filename:SKILL.md"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            items = data.get("items", [])
            if items:
                # Extract unique parent directories from SKILL.md paths
                seen_paths = set()
                for item in items:
                    path = item.get("path", "")
                    if path.endswith("SKILL.md"):
                        # Get parent directory (skill folder)
                        parent = "/".join(path.split("/")[:-1])
                        if parent and parent not in seen_paths:
                            seen_paths.add(parent)
                            skill_name = parent.split("/")[-1]
                            found_skills.append({"name": skill_name, "path": parent})
                
                if found_skills:
                    print(f"  📂 Found {len(found_skills)} skills via Code Search")
                    for skill in found_skills:
                        print(f"    - {skill['name']} ({skill['path']})")
    except subprocess.TimeoutExpired:
        print("  ⚠️ Code Search timeout, falling back to directory scan...")
    except Exception as e:
        print(f"  ⚠️ Code Search failed ({e}), falling back to directory scan...")
    
    # Method 2: Fallback to directory-based search if Code Search fails or returns empty
    if not found_skills:
        # Check common skill directories
        skills_paths = ["skills", ".github/skills", ".claude/skills", "scientific-skills"]
        found_in_subdir = False
        
        for path in skills_paths:
            try:
                result = subprocess.run(
                    ["gh", "api", f"repos/{repo_full}/contents/{path}"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0 and "message" not in result.stdout[:50]:
                    items = json.loads(result.stdout)
                    if isinstance(items, list):
                        print(f"  📂 Found {len(items)} items in {path}")
                        for item in items:
                            name = item.get("name", "")
                            if name and item.get("type") == "dir":
                                found_skills.append({"name": name, "path": f"{path}/{name}"})
                                print(f"    - {name}")
                        found_in_subdir = True
                        break
            except subprocess.TimeoutExpired:
                print(f"  ⚠️ Timeout checking {path}")
            except FileNotFoundError:
                print("  ❌ GitHub CLI (gh) not found.")
                break
            except Exception:
                # Silently ignore other errors (JSON parse errors, network issues, etc.)
                # and continue checking other paths
                pass
        
        # If no skills/ directory found, check root for SKILL.md in subdirectories
        if not found_in_subdir:
            try:
                result = subprocess.run(
                    ["gh", "api", f"repos/{repo_full}/contents"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    items = json.loads(result.stdout)
                    if isinstance(items, list):
                        dirs = [item for item in items if item.get("type") == "dir"]
                        skill_dirs = []
                        for d in dirs:
                            name = d.get("name", "")
                            if name.startswith(".") or name in ["docs", "examples", "tests", "node_modules", "dist", "build"]:
                                continue
                            check_result = subprocess.run(
                                ["gh", "api", f"repos/{repo_full}/contents/{name}/SKILL.md"],
                                capture_output=True, text=True, timeout=5
                            )
                            if check_result.returncode == 0 and "message" not in check_result.stdout[:50]:
                                skill_dirs.append({"name": name, "path": name})
                        
                        if skill_dirs:
                            print(f"  📂 Found {len(skill_dirs)} skills at root level")
                            for skill in skill_dirs:
                                found_skills.append(skill)
                                print(f"    - {skill['name']}")
            except subprocess.TimeoutExpired:
                print("  ⚠️ Timeout checking root")
            except Exception:
                # Silently ignore errors when checking root directory
                # (e.g., rate limits, permission issues)
                pass

    # Add found skills to index
    if found_skills:
        print("\n✨ Adding skills to index...")
        added = 0
        for skill in found_skills:
            existing = [s for s in index["skills"] 
                       if s["name"] == skill["name"] and s["source"] == source_id]
            if not existing:
                index["skills"].append({
                    "name": skill["name"],
                    "source": source_id,
                    "path": skill["path"],
                    "categories": ["community"],
                    "description": f"{skill['name']} skill"
                })
                print(f"  ✅ {skill['name']}")
                added += 1
            else:
                print(f"  ⏭️ {skill['name']} (exists)")
        if added > 0:
            save_index(index)
    else:
        print("  ⚠️ No skills found")


def update_all_sources() -> None:
    """Update skills from all registered sources."""
    index = load_index()
    if not index:
        return
    
    print("🔄 Updating all sources...")
    sources = index.get("sources", [])
    
    for src in sources:
        url = src.get("url", "")
        match = re.search(r"github\.com/([^/]+/[^/]+)", url)
        if match:
            repo_full = match.group(1)
            print(f"\n📦 {src['id']} ({repo_full})")
            update_source_skills(index, src["id"], repo_full)
    
    print("\n✅ Update complete!")


# =============================================================================
# Skill Info & Install
# =============================================================================

def show_skill_info(skill_name: str) -> None:
    """Show detailed information about a skill."""
    index = load_index()
    if not index:
        return
    
    # Find skill
    skills = [s for s in index.get("skills", []) if s["name"].lower() == skill_name.lower()]
    if not skills:
        print(f"❌ Skill not found: {skill_name}")
        # Suggest similar
        similar = find_similar_skills(index, skill_name)
        if similar:
            print("\n💡 Did you mean:")
            for s in similar[:5]:
                print(f"  - {s['name']}")
        return
    
    skill = skills[0]
    sources = {s["id"]: s for s in index.get("sources", [])}
    src = sources.get(skill.get("source"), {})
    
    print(f"\n📦 {skill['name']}")
    print("=" * 50)
    print(f"📝 Description: {skill.get('description', 'N/A')}")
    print(f"📁 Source: {src.get('name', skill.get('source', 'Unknown'))}")
    print(f"🏷️  Categories: {', '.join(skill.get('categories', []))}")
    print(f"📂 Path: {skill.get('path', 'N/A')}")
    
    url = src.get("url", "")
    path = skill.get("path", "")
    if url and path:
        full_url = f"{url}/tree/main/{path}"
        print(f"🔗 URL: {full_url}")
    
    # Try to fetch SKILL.md content
    if url and path:
        print("\n📄 Fetching SKILL.md...")
        match = re.search(r"github\.com/([^/]+/[^/]+)", url)
        if match:
            repo_full = match.group(1)
            try:
                result = subprocess.run(
                    ["gh", "api", f"repos/{repo_full}/contents/{path}/SKILL.md", 
                     "-H", "Accept: application/vnd.github.raw"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    print("\n" + "-" * 50)
                    # Show first 50 lines
                    lines = result.stdout.split('\n')[:50]
                    print('\n'.join(lines))
                    if len(result.stdout.split('\n')) > 50:
                        print("\n... (truncated)")
            except Exception as e:
                print(f"  ⚠️ Could not fetch: {e}")


def install_skill(skill_name: str, target_dir: str = None) -> None:
    """Install a skill to local directory."""
    index = load_index()
    if not index:
        return
    
    # Find skill
    skills = [s for s in index.get("skills", []) if s["name"].lower() == skill_name.lower()]
    if not skills:
        print(f"❌ Skill not found: {skill_name}")
        return
    
    skill = skills[0]
    sources = {s["id"]: s for s in index.get("sources", [])}
    src = sources.get(skill.get("source"), {})
    url = src.get("url", "")
    path = skill.get("path", "")
    
    if not url or not path:
        print(f"❌ Cannot install: missing URL or path information")
        return
    
    # Determine target directory
    if target_dir:
        install_path = Path(target_dir) / skill["name"]
    else:
        install_path = INSTALL_DIR / skill["name"]
    
    match = re.search(r"github\.com/([^/]+/[^/]+)", url)
    if not match:
        print(f"❌ Invalid source URL")
        return
    
    repo_full = match.group(1)
    
    print(f"📥 Installing {skill['name']}...")
    print(f"   From: {url}")
    print(f"   To: {install_path}")
    
    # Create directory
    install_path.mkdir(parents=True, exist_ok=True)
    
    # Download files using gh CLI
    try:
        # Get file list
        result = subprocess.run(
            ["gh", "api", f"repos/{repo_full}/contents/{path}"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            print(f"❌ Failed to list files: {result.stderr}")
            return
        
        items = json.loads(result.stdout)
        if not isinstance(items, list):
            items = [items]
        
        # Download each file
        for item in items:
            if item.get("type") == "file":
                file_name = item.get("name", "")
                download_url = item.get("download_url", "")
                if file_name and download_url:
                    print(f"   📄 {file_name}")
                    # Use curl
                    file_path = install_path / file_name
                    dl_result = subprocess.run(
                        ["curl", "-sL", "-o", str(file_path), download_url],
                        timeout=30
                    )
                    if dl_result.returncode != 0:
                        print(f"      ⚠️ Failed to download")
        
        print(f"\n✅ Installed to: {install_path}")
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")


# =============================================================================
# Star Management
# =============================================================================

def star_skill(skill_name: str, unstar: bool = False) -> None:
    """Star or unstar a skill."""
    index = load_index()
    if not index:
        return
    
    # Find skill
    skills = [s for s in index.get("skills", []) if s["name"].lower() == skill_name.lower()]
    if not skills:
        print(f"❌ Skill not found: {skill_name}")
        return
    
    skill = skills[0]
    skill_id = f"{skill['source']}/{skill['name']}"
    
    starred = load_stars()
    
    if unstar:
        if skill_id in starred:
            starred.remove(skill_id)
            save_stars(starred)
            print(f"☆ Unstarred: {skill['name']}")
        else:
            print(f"⚠️ Skill is not starred: {skill['name']}")
    else:
        if skill_id not in starred:
            starred.append(skill_id)
            save_stars(starred)
            print(f"⭐ Starred: {skill['name']}")
        else:
            print(f"⚠️ Already starred: {skill['name']}")


def list_starred() -> None:
    """List all starred skills."""
    starred = load_stars()
    if not starred:
        print("☆ No starred skills yet.")
        print("  Use --star <skill-name> to star a skill.")
        return
    
    print(f"\n⭐ Starred Skills ({len(starred)}):")
    for skill_id in starred:
        print(f"  - {skill_id}")


# =============================================================================
# Similar Skills & Recommendations
# =============================================================================

def find_similar_skills(index: Dict, skill_name: str, limit: int = 5) -> List[Dict]:
    """Find skills similar to the given skill name or query."""
    skills = index.get("skills", [])
    
    # First try to find the exact skill
    target_skill = None
    for s in skills:
        if s["name"].lower() == skill_name.lower():
            target_skill = s
            break
    
    if target_skill:
        # Find by matching categories
        target_cats = set(target_skill.get("categories", []))
        similar = []
        for s in skills:
            if s["name"] != target_skill["name"]:
                s_cats = set(s.get("categories", []))
                overlap = len(target_cats & s_cats)
                if overlap > 0:
                    similar.append((overlap, s))
        similar.sort(key=lambda x: -x[0])
        return [s[1] for s in similar[:limit]]
    else:
        # Fuzzy match by name
        query_lower = skill_name.lower()
        similar = []
        for s in skills:
            name_lower = s["name"].lower()
            # Simple similarity: count matching characters
            score = sum(1 for c in query_lower if c in name_lower)
            if score > 0:
                similar.append((score, s))
        similar.sort(key=lambda x: -x[0])
        return [s[1] for s in similar[:limit]]


def show_similar(skill_name: str) -> None:
    """Show skills similar to the given skill."""
    index = load_index()
    if not index:
        return
    
    similar = find_similar_skills(index, skill_name)
    if similar:
        print(f"\n💡 Skills similar to '{skill_name}':")
        for s in similar:
            print(f"  - {s['name']} ({', '.join(s.get('categories', [])[:3])})")
    else:
        print(f"  No similar skills found.")


# =============================================================================
# Post-Search Suggestions
# =============================================================================

def show_post_search_suggestions(index: Dict, query: str, results: List[Dict]) -> None:
    """Show helpful suggestions after search."""
    print("\n" + "━" * 50)
    print("💡 Suggestions")
    
    # 1. Related categories
    if results:
        all_categories = set()
        for r in results[:3]:
            all_categories.update(r.get("categories", []))
        if all_categories:
            cats_str = ", ".join(list(all_categories)[:3])
            print(f"  🏷️ Related categories: {cats_str}")
            print(f"     → Example: python scripts/search_skills.py \"#{list(all_categories)[0]}\"")
    
    # 2. Similar skills
    similar = find_similar_skills(index, query, limit=3)
    unshown = [s for s in similar if s not in results]
    if unshown:
        print(f"\n  🔍 You might also like:")
        for s in unshown[:3]:
            print(f"     - {s['name']}: {s.get('description', '')[:40]}")
    
    # 3. Starred skills count
    starred = load_stars()
    if starred and len(starred) > 0:
        print(f"\n  ⭐ Your favorites: {len(starred)} skills")


def prompt_discover_new_repos(query: str) -> None:
    """Ask user if they want to discover new repositories."""
    print("\n" + "━" * 50)
    try:
        answer = input("🌐 Search for more repositories? [y/N]: ").strip().lower()
        if answer in ["y", "yes"]:
            print("\n🔍 Searching GitHub for related repositories...")
            discover_new_repos(query)
    except (EOFError, KeyboardInterrupt):
        print("\n  Skipped")


def discover_new_repos(query: str) -> None:
    """Search for new skill repositories on GitHub."""
    search_terms = f"{query} SKILL.md agent skills" if query else "SKILL.md agent skills claude copilot"
    
    try:
        # Repository search
        result = subprocess.run(
            ["gh", "search", "repos", search_terms, "--json", "nameWithOwner,description,stargazersCount", "--limit", "10"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            repos = json.loads(result.stdout)
            if repos:
                print(f"\n📦 Found {len(repos)} repositories:")
                for i, repo in enumerate(repos, 1):
                    name = repo.get("nameWithOwner", "")
                    desc = repo.get("description", "")[:50] or "No description"
                    stars = repo.get("stargazersCount", 0)
                    print(f"\n  [{i}] {name} ⭐{stars}")
                    print(f"      {desc}")
                
                # Ask to add to index
                print("\n" + "-" * 40)
                try:
                    choice = input("📥 Enter repository number to add (blank to skip): ").strip()
                    if choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(repos):
                            repo_name = repos[idx].get("nameWithOwner", "")
                            add_source(f"https://github.com/{repo_name}")
                except (EOFError, KeyboardInterrupt):
                    pass  # User cancelled input, skip adding repository
            else:
                print("  No matching repositories found")
        else:
            print(f"  ⚠️ Search failed: {result.stderr}")
    except FileNotFoundError:
        print("  ⚠️ GitHub CLI (gh) not found")
    except subprocess.TimeoutExpired:
        print("  ⚠️ Search timed out")
    except Exception as e:
        print(f"  ⚠️ Error: {e}")


# =============================================================================
# Statistics
# =============================================================================

def show_statistics() -> None:
    """Show skill index statistics."""
    index = load_index()
    if not index:
        return
    
    skills = index.get("skills", [])
    sources = index.get("sources", [])
    categories = index.get("categories", [])
    starred = load_stars()
    
    print("\n📊 Skill Index Statistics")
    print("=" * 50)
    print(f"📅 Last Updated: {index.get('lastUpdated', 'Unknown')}")
    print(f"📦 Total Skills: {len(skills)}")
    print(f"📁 Sources: {len(sources)}")
    print(f"🏷️  Categories: {len(categories)}")
    print(f"⭐ Starred: {len(starred)}")
    
    # Skills per source
    print("\n📦 Skills by Source:")
    source_counts = {}
    for s in skills:
        src = s.get("source", "unknown")
        source_counts[src] = source_counts.get(src, 0) + 1
    for src, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"  {src}: {count}")
    
    # Skills per category
    print("\n🏷️  Skills by Category:")
    cat_counts = {}
    for s in skills:
        for cat in s.get("categories", []):
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {cat}: {count}")


# =============================================================================
# Dependency Check
# =============================================================================

def check_dependencies() -> None:
    """Check if required tools are installed."""
    print("\n🔧 Checking Dependencies...")
    
    tools = [
        ("gh", "gh", "GitHub CLI - Required for external search and install"),
        ("curl", "curl", "cURL - Required for downloading files"),
        ("python", sys.executable, "Python 3 - You're running this!"),
    ]
    
    for label, executable, desc in tools:
        try:
            result = subprocess.run([executable, "--version"], capture_output=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.decode().split('\n')[0][:50]
                print(f"  ✅ {label}: {version}")
            else:
                print(f"  ❌ {label}: Not working properly")
        except FileNotFoundError:
            print(f"  ❌ {label}: Not found - {desc}")
        except Exception as e:
            print(f"  ⚠️ {label}: Error - {e}")


# =============================================================================
# Output Functions
# =============================================================================

def print_results(results: List[Dict], title: str) -> None:
    """Print search results."""
    print(f"\n📋 {title}:")
    for i, skill in enumerate(results, 1):
        star = "⭐" if skill.get("starred") else ""
        print(f"\n[{i}] {skill['name']} {star}")
        print(f"    📝 {skill.get('description', '')}")
        print(f"    📦 {skill.get('sourceName', skill.get('source', ''))}")
        print(f"    🏷️  {', '.join(skill.get('categories', []))}")
        url = skill.get('sourceUrl', '')
        path = skill.get('path', '')
        if url and path:
            print(f"    🔗 {url}/{path}")


def list_categories(index: Dict) -> None:
    """List available categories."""
    print("\n📁 Available Categories:")
    for cat in index.get("categories", []):
        print(f"  {cat['id']} - {cat.get('description', cat.get('name', ''))}")


def list_sources(index: Dict) -> None:
    """List available sources."""
    print("\n📦 Available Sources:")
    for src in index.get("sources", []):
        print(f"  {src['id']} [{src.get('type', 'community')}]")
        print(f"    {src.get('name', '')} - {src.get('url', '')}")


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Skill Finder - Search and manage Agent Skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "pdf"                    Search for skills
  %(prog)s "#azure #bicep"          Search by tags
  %(prog)s --category development   Filter by category
  %(prog)s --info skill-name        Show skill details
  %(prog)s --install skill-name     Install skill locally
  %(prog)s --star skill-name        Star a skill
  %(prog)s --similar skill-name     Find similar skills
  %(prog)s --update                 Update all sources
  %(prog)s --stats                  Show statistics
        """
    )
    
    # Search arguments
    parser.add_argument("query", nargs="?", default="", help="Search keyword (supports #tags)")
    parser.add_argument("--category", "-c", help="Filter by category")
    parser.add_argument("--source", "-s", help="Filter by source")
    parser.add_argument("--external", "-e", action="store_true", help="Also search GitHub")
    parser.add_argument("--web", "-w", action="store_true", help="Show web search URLs")
    
    # List arguments
    parser.add_argument("--list-categories", action="store_true", help="List categories")
    parser.add_argument("--list-sources", action="store_true", help="List sources")
    parser.add_argument("--list-starred", action="store_true", help="List starred skills")
    
    # Management arguments
    parser.add_argument("--add-source", metavar="URL", help="Add a new source repository")
    parser.add_argument("--update", action="store_true", help="Update all sources")
    
    # Skill actions
    parser.add_argument("--info", metavar="SKILL", help="Show skill details")
    parser.add_argument("--install", metavar="SKILL", help="Install skill locally")
    parser.add_argument("--install-dir", metavar="DIR", help="Installation directory")
    parser.add_argument("--star", metavar="SKILL", help="Star a skill")
    parser.add_argument("--unstar", metavar="SKILL", help="Unstar a skill")
    parser.add_argument("--similar", metavar="SKILL", help="Find similar skills")
    
    # Other
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--check", action="store_true", help="Check dependencies")
    parser.add_argument("--no-interactive", action="store_true", 
                        help="Disable interactive prompts (for CI/automation)")
    
    args = parser.parse_args()
    
    # Action handlers
    if args.check:
        check_dependencies()
        return
    
    if args.add_source:
        add_source(args.add_source)
        return
    
    if args.update:
        update_all_sources()
        return
    
    if args.info:
        show_skill_info(args.info)
        return
    
    if args.install:
        install_skill(args.install, args.install_dir)
        return
    
    if args.star:
        star_skill(args.star)
        return
    
    if args.unstar:
        star_skill(args.unstar, unstar=True)
        return
    
    if args.list_starred:
        list_starred()
        return
    
    if args.similar:
        show_similar(args.similar)
        return
    
    if args.stats:
        show_statistics()
        return
    
    # Load index
    index = load_index()
    if not index:
        sys.exit(1)
    
    # 自動更新チェック（1週間以上経過していたら）
    if not args.no_interactive:
        index = check_and_auto_update(index)
    
    # List mode
    if args.list_categories:
        list_categories(index)
        return
    
    if args.list_sources:
        list_sources(index)
        return
    
    # Search mode
    print("\n🔍 Searching skills...")
    
    # Local search
    local_results = search_local(index, args.query, args.category, args.source)
    
    if local_results:
        print_results(local_results, f"Found {len(local_results)} skills in local index")
    else:
        print("  No matches in local index")
    
    # External search
    external_found = False
    if not local_results or args.external:
        github_results = search_github(args.query)
        if github_results:
            external_found = True
            print(f"\n🌐 Found {len(github_results)} on GitHub:")
            for i, item in enumerate(github_results, 1):
                repo = item.get("repository", {}).get("nameWithOwner", "")
                print(f"\n[{i}] {repo}")
                print(f"    📄 {item.get('path', '')}")
                print(f"    🔗 https://github.com/{repo}")
            print("\n💡 Tip: Use --add-source to add good repos to your index")
        else:
            print("\n  No matches on GitHub")
    
    # Web search fallback
    if not local_results and not external_found and args.query:
        print("\n" + "━" * 50)
        print("📭 No matches found. Try web search:")
        show_web_search_urls(args.query)
    
    if args.web:
        show_web_search_urls(args.query)
    
    # Show similar if few results
    if args.query and len(local_results) < 3:
        similar = find_similar_skills(index, args.query, limit=3)
        if similar:
            print(f"\n💡 You might also like:")
            for s in similar:
                if s not in local_results:
                    print(f"  - {s['name']}")
    
    # 検索後のサジェスト表示
    if args.query:
        show_post_search_suggestions(index, args.query, local_results)
    
    # 他のリポジトリを探すか聞く（ローカル結果が少ない場合、インタラクティブモード時のみ）
    if args.query and len(local_results) < 5 and not args.external and not args.no_interactive:
        prompt_discover_new_repos(args.query)


if __name__ == "__main__":
    main()
