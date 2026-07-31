import json
import datetime
import os
import re

def load_data(filepath="data.json"):
    """Load and parse the JSON data source."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Source data file '{filepath}' not found.")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def get_today_ist():
    """Get today's date in IST (UTC+5:30) matching the user's environment."""
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    ist_offset = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    return utc_now.astimezone(ist_offset).date()

def calculate_streaks(upload_dates, today):
    """
    Calculate current and longest upload streaks based on upload dates.
    upload_dates: list of datetime.date objects
    """
    if not upload_dates:
        return 0, 0

    sorted_dates = sorted(list(set(upload_dates)))

    # Longest streak calculation
    longest = 0
    current_temp = 0
    prev_date = None

    for d in sorted_dates:
        if prev_date is None:
            current_temp = 1
        elif (d - prev_date).days == 1:
            current_temp += 1
        elif (d - prev_date).days > 1:
            if current_temp > longest:
                longest = current_temp
            current_temp = 1
        prev_date = d
    if current_temp > longest:
        longest = current_temp

    # Current streak calculation
    current_streak = 0
    if today in sorted_dates:
        current_streak = 1
        check_date = today - datetime.timedelta(days=1)
        while check_date in sorted_dates:
            current_streak += 1
            check_date -= datetime.timedelta(days=1)
    elif (today - datetime.timedelta(days=1)) in sorted_dates:
        current_streak = 1
        check_date = today - datetime.timedelta(days=2)
        while check_date in sorted_dates:
            current_streak += 1
            check_date -= datetime.timedelta(days=1)

    return current_streak, longest

def generate_quick_access(drive_folder, uploads):
    """Generate the top badge buttons for quick access."""
    latest_upload_url = drive_folder
    if uploads:
        # Sort to get the latest
        sorted_uploads = sorted(uploads, key=lambda x: x["date"], reverse=True)
        latest_upload_url = sorted_uploads[0].get("drive_link", drive_folder)

    # Repository URL
    repo_url = "https://github.com/Vijay-Junoon/DSA-Course"

    drive_badge = f"[![Google Drive](https://img.shields.io/badge/📂_Open_Google_Drive-12878D?style=for-the-badge&logo=googledrive&logoColor=white)]({drive_folder})"
    star_badge = f"[![Star Repo](https://img.shields.io/badge/⭐_Star_Repository-orange?style=for-the-badge)]({repo_url})"
    latest_badge = f"[![Latest Upload](https://img.shields.io/badge/📅_Latest_Upload-blue?style=for-the-badge)]({latest_upload_url})"
    archive_badge = f"[![Browse Archive](https://img.shields.io/badge/📚_Browse_Archive-purple?style=for-the-badge)](#-monthly-archive)"

    return f"{drive_badge} &nbsp; {star_badge} &nbsp; {latest_badge} &nbsp; {archive_badge}"

def generate_statistics_badges(stats):
    """Generate Shields.io badges for the statistics overview."""
    badges = [
        ("Total Upload Days", f"{stats['total_days']} Days", "blue", "calendar"),
        ("Current Streak", f"{stats['current_streak']} Days", "orange", "fire"),
        ("Longest Streak", f"{stats['longest_streak']} Days", "red", "trophy"),
        ("Total Resources", f"{stats['total_resources']}", "brightgreen", "google-drive"),
        ("PDFs Shared", f"{stats['total_pdfs']}", "critical", "adobe-acrobat-reader"),
        ("Videos Shared", f"{stats['total_videos']}", "blueviolet", "youtube"),
        ("Notes Shared", f"{stats['total_notes']}", "yellow", "read-the-docs"),
        ("LeetCode Solved", f"{stats['leetcode_count']}", "yellowgreen", "leetcode"),
        ("SQL Resources", f"{stats['total_sql']}", "lightblue", "mysql"),
        ("Python Resources", f"{stats['total_python']}", "lightgrey", "python"),
        ("Topics Covered", f"{stats['total_topics']}", "purple", "bookstack"),
    ]

    badge_mds = []
    for label, val, color, logo in badges:
        label_escaped = label.replace(" ", "%20")
        val_escaped = val.replace(" ", "%20")
        badge_mds.append(f"![{label}](https://img.shields.io/badge/{label_escaped}-{val_escaped}-{color}?style=flat-square&logo={logo})")

    # Arrange in a beautiful markdown table grid
    grid = (
        "| | | |\n"
        "| :---: | :---: | :---: |\n"
        f"| {badge_mds[0]} | {badge_mds[1]} | {badge_mds[2]} |\n"
        f"| {badge_mds[3]} | {badge_mds[4]} | {badge_mds[5]} |\n"
        f"| {badge_mds[6]} | {badge_mds[7]} | {badge_mds[8]} |\n"
        f"| {badge_mds[9]} | {badge_mds[10]} | |"
    )
    return grid

def generate_latest_uploads_table(uploads):
    """Generate markdown table for the 10 most recent uploads."""
    sorted_uploads = sorted(uploads, key=lambda x: x["date"], reverse=True)[:10]

    table_header = (
        "| Date | Topic | Category | Resource | Drive Link |\n"
        "| :--- | :--- | :--- | :--- | :--- |\n"
    )

    rows = []
    for item in sorted_uploads:
        # Format date to DD MMM YYYY
        dt = datetime.datetime.strptime(item["date"], "%Y-%m-%d")
        formatted_date = dt.strftime("%d %b %Y")

        # Resource details (include difficulty emoji and leetcode if available)
        diff_emoji = ""
        diff = item.get("difficulty", "N/A")
        if diff == "Easy":
            diff_emoji = "🟢 "
        elif diff == "Medium":
            diff_emoji = "🟡 "
        elif diff == "Hard":
            diff_emoji = "🔴 "

        resource_title = item["title"]
        if item.get("leetcode_id"):
            resource_title = f"{resource_title} (`{item['leetcode_id']}`)"

        resource_str = f"{diff_emoji}{resource_title} *({item['resource_type']})*"
        drive_link = f"[🔗 View Resource]({item['drive_link']})"

        rows.append(f"| {formatted_date} | {item['topic']} | {item['category']} | {resource_str} | {drive_link} |")

    return table_header + "\n".join(rows)

def generate_learning_progress(uploads):
    """Generate text progress bars for major DSA/programming topics."""
    # List of major topics to show progress
    major_topics = [
        "Arrays", "Two Pointers", "Strings", "Hashing", "Linked Lists", "Stacks", "Queues",
        "Trees", "BST", "Heaps", "Graphs", "Dynamic Programming", "Greedy",
        "Backtracking", "Bit Manipulation", "SQL", "Python"
    ]

    # Benchmarks for 100% completion (target number of uploads per topic)
    TOPIC_TARGETS = {
        "Arrays": 8,
        "Two Pointers": 6,
        "Strings": 6,
        "Hashing": 5,
        "Linked Lists": 8,
        "Stacks": 5,
        "Queues": 5,
        "Trees": 8,
        "BST": 4,
        "Heaps": 4,
        "Graphs": 8,
        "Dynamic Programming": 10,
        "Greedy": 6,
        "Backtracking": 5,
        "Bit Manipulation": 4,
        "SQL": 10,
        "Python": 10
    }

    # Count resources per topic (case-insensitive categorization mapping)
    counts = {topic: 0 for topic in major_topics}
    for item in uploads:
        cat = item.get("category", "")
        # Try direct match
        matched = False
        for topic in major_topics:
            if cat.lower() == topic.lower():
                counts[topic] += 1
                matched = True
                break
        if not matched:
            # Try matching with topic field
            topic_field = item.get("topic", "")
            for topic in major_topics:
                if topic.lower() in topic_field.lower():
                    counts[topic] += 1
                    break

    progress_lines = []
    progress_lines.append("```text")
    for topic in major_topics:
        count = counts[topic]
        target = TOPIC_TARGETS.get(topic, 5)
        pct = min(100, int((count / target) * 100))

        # 10 character bar
        filled_chars = min(10, int(pct / 10))
        empty_chars = 10 - filled_chars
        bar = "█" * filled_chars + "░" * empty_chars

        # Alignment
        topic_padded = f"{topic:<20}"
        progress_lines.append(f"{topic_padded} {bar} {pct}% ({count}/{target})")
    progress_lines.append("```")

    return "\n".join(progress_lines)

def generate_topic_statistics(uploads):
    """Generate topic statistics count table."""
    counts = {}
    for item in uploads:
        topic = item.get("topic", "Unknown")
        counts[topic] = counts.get(topic, 0) + 1

    sorted_topics = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    table = "| Topic | Resources |\n| :--- | ---: |\n"
    for topic, count in sorted_topics:
        table += f"| {topic} | {count} |\n"
    return table

def generate_difficulty_distribution(uploads):
    """Generate difficulty distribution table with indicators."""
    counts = {"Easy": 0, "Medium": 0, "Hard": 0, "N/A": 0}
    for item in uploads:
        diff = item.get("difficulty", "N/A")
        if diff in counts:
            counts[diff] += 1
        else:
            counts["N/A"] += 1

    table = "| Difficulty | Count |\n| :--- | ---: |\n"
    table += f"| 🟢 Easy | {counts['Easy']} |\n"
    table += f"| 🟡 Medium | {counts['Medium']} |\n"
    table += f"| 🔴 Hard | {counts['Hard']} |\n"
    if counts["N/A"] > 0:
        table += f"| ⚪ N/A | {counts['N/A']} |\n"
    return table

def generate_resource_type_distribution(uploads):
    """Generate resource type distribution table."""
    counts = {}
    for item in uploads:
        rt = item.get("resource_type", "Other")
        counts[rt] = counts.get(rt, 0) + 1

    sorted_rt = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    table = "| Resource Type | Count |\n| :--- | ---: |\n"
    for rt, count in sorted_rt:
        table += f"| {rt} | {count} |\n"
    return table

def generate_recent_activity(uploads, today):
    """Generate 30 days activity tracker calendar grid/columns."""
    upload_set = {item["date"] for item in uploads}

    activity_items = []
    for i in range(29, -1, -1):
        day = today - datetime.timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        label = day.strftime("%b %d")

        if day_str in upload_set:
            activity_items.append(f"✅ {label}")
        else:
            activity_items.append(f"⬜ {label}")

    # Arrange in a clean 3-column text preformatted layout to save vertical space
    cols = [[], [], []]
    for idx, act in enumerate(activity_items):
        cols[idx % 3].append(act)

    lines = []
    lines.append("```text")
    for r in range(len(cols[0])):
        row_str = ""
        for c in range(3):
            if r < len(cols[c]):
                row_str += f"{cols[c][r]:<18}"
        lines.append(row_str.rstrip())
    lines.append("```")

    return "\n".join(lines)

def generate_monthly_archive(uploads):
    """Generate collapsible archive sections grouped by month."""
    # Group by Year-Month
    archive = {}
    for item in uploads:
        dt = datetime.datetime.strptime(item["date"], "%Y-%m-%d")
        year_month = dt.strftime("%Y-%m")
        if year_month not in archive:
            archive[year_month] = []
        archive[year_month].append(item)

    # Sort months descending
    sorted_months = sorted(archive.keys(), reverse=True)

    archive_md = []
    for ym in sorted_months:
        dt = datetime.datetime.strptime(ym, "%Y-%m")
        month_name = dt.strftime("%B %Y")
        items = archive[ym]

        # Sort items inside month descending by date
        sorted_items = sorted(items, key=lambda x: x["date"], reverse=True)

        archive_md.append(f"<details>")
        archive_md.append(f"<summary>📅 {month_name} ({len(items)} resources)</summary>\n")

        for item in sorted_items:
            idt = datetime.datetime.strptime(item["date"], "%Y-%m-%d")
            day_str = idt.strftime("%d %b")

            diff = item.get("difficulty", "N/A")
            diff_str = f" [{diff}]" if diff != "N/A" else ""

            resource_info = f"{item['title']} ({item['category']}{diff_str})"
            if item.get("leetcode_id"):
                resource_info += f" - LeetCode: {item['leetcode_id']}"

            archive_md.append(f"- **{day_str}** — {resource_info} — [🔗 Drive Link]({item['drive_link']})")

        archive_md.append(f"\n</details>")

    return "\n".join(archive_md)

def generate_drive_section(drive_folder):
    """Generate the prominent Google Drive button and details."""
    btn = (
        f'<p align="center">\n'
        f'  <a href="{drive_folder}" target="_blank">\n'
        f'    <img src="https://img.shields.io/badge/Access_Google_Drive_Folder-12878D?style=for-the-badge&logo=googledrive&logoColor=white" alt="Google Drive Button" height="40">\n'
        f'  </a>\n'
        f'</p>'
    )
    note = (
        "\n> [!NOTE]\n"
        "> All learning resources are stored on Google Drive. The repository serves as an organized public index for easy navigation."
    )
    return btn + note

def main():
    print("Loading data.json...")
    data = load_data()
    drive_folder = data.get("drive_folder", "")
    uploads = data.get("uploads", [])

    today = get_today_ist()
    print(f"Current Date (IST): {today}")

    # Parse all upload dates
    upload_dates = []
    for item in uploads:
        try:
            d = datetime.datetime.strptime(item["date"], "%Y-%m-%d").date()
            upload_dates.append(d)
        except ValueError:
            print(f"Warning: Invalid date format in record: {item}")

    print("Calculating streaks...")
    current_streak, longest_streak = calculate_streaks(upload_dates, today)
    print(f"Current Streak: {current_streak}, Longest Streak: {longest_streak}")

    # Calculate count statistics
    total_resources = len(uploads)
    total_pdfs = sum(1 for x in uploads if x.get("resource_type", "").lower() == "pdf")
    total_videos = sum(1 for x in uploads if x.get("resource_type", "").lower() == "video")
    total_notes = sum(1 for x in uploads if x.get("resource_type", "").lower() in ["notes", "revision notes", "cheat sheet"])
    leetcode_count = sum(1 for x in uploads if x.get("leetcode_id") is not None and x.get("leetcode_id") != "")
    total_sql = sum(1 for x in uploads if x.get("category", "").lower() == "sql")
    total_python = sum(1 for x in uploads if x.get("category", "").lower() == "python")
    total_topics = len(set(x.get("topic", "") for x in uploads if x.get("topic")))
    total_days = len(set(upload_dates))

    stats = {
        "total_days": total_days,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_resources": total_resources,
        "total_pdfs": total_pdfs,
        "total_videos": total_videos,
        "total_notes": total_notes,
        "leetcode_count": leetcode_count,
        "total_sql": total_sql,
        "total_python": total_python,
        "total_topics": total_topics
    }

    # Generate Markdown sections
    print("Generating markdown sections...")
    quick_access = generate_quick_access(drive_folder, uploads)
    stats_badges = generate_statistics_badges(stats)
    latest_uploads = generate_latest_uploads_table(uploads)
    learning_progress = generate_learning_progress(uploads)
    topic_stats = generate_topic_statistics(uploads)
    difficulty_dist = generate_difficulty_distribution(uploads)
    resource_dist = generate_resource_type_distribution(uploads)
    recent_activity = generate_recent_activity(uploads, today)
    monthly_archive = generate_monthly_archive(uploads)
    drive_section = generate_drive_section(drive_folder)

    # Read template
    print("Reading README_template.md...")
    with open("README_template.md", "r", encoding="utf-8") as f:
        template = f.read()

    # Replace placeholders
    print("Replacing placeholders...")
    readme_content = template
    readme_content = readme_content.replace("<!-- {{QUICK_ACCESS}} -->", quick_access)
    readme_content = readme_content.replace("<!-- {{STATISTICS}} -->", stats_badges)
    readme_content = readme_content.replace("<!-- {{LATEST_UPLOADS}} -->", latest_uploads)
    readme_content = readme_content.replace("<!-- {{LEARNING_PROGRESS}} -->", learning_progress)
    readme_content = readme_content.replace("<!-- {{TOPIC_STATISTICS}} -->", topic_stats)
    readme_content = readme_content.replace("<!-- {{DIFFICULTY_DISTRIBUTION}} -->", difficulty_dist)
    readme_content = readme_content.replace("<!-- {{RESOURCE_TYPE_DISTRIBUTION}} -->", resource_dist)
    readme_content = readme_content.replace("<!-- {{RECENT_ACTIVITY}} -->", recent_activity)
    readme_content = readme_content.replace("<!-- {{MONTHLY_ARCHIVE}} -->", monthly_archive)
    readme_content = readme_content.replace("<!-- {{DRIVE_SECTION}} -->", drive_section)

    # Update last updated timestamp (IST)
    now_ist_str = datetime.datetime.now(datetime.timezone.utc).astimezone(
        datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    ).strftime("%d %b %Y %I:%M %p IST")
    readme_content = readme_content.replace("<!-- {{LAST_UPDATED}} -->", now_ist_str)

    # Write output
    print("Writing README.md...")
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("README.md generated successfully!")

if __name__ == "__main__":
    main()
