import os

constants_path = r"C:\Users\ayanm\AndroidStudioProjects\CampusConnectStudent\app\src\main\java\com\campusconnect\student\utils\Constants.kt"
constants_content = """package com.campusconnect.student.utils

object Constants {
    // API
    const val BASE_URL = "https://c1-8av0.onrender.com/"
    const val API_TIMEOUT = 30L

    // Preferences
    const val PREFS_NAME = "campus_connect_prefs"
    const val KEY_AUTH_TOKEN = "auth_token"
    const val KEY_STUDENT_ID = "student_id"

    // Database
    const val DATABASE_NAME = "campus_connect_db"

    /**
     * Resolves raw photo or document paths (e.g. relative static uploads)
     * to a fully qualified URL accessible by Coil/Glide.
     */
    fun getFullImageUrl(rawUrl: String?): String? {
        if (rawUrl.isNullOrBlank()) return null
        val trimmed = rawUrl.trim()
        if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
            return trimmed
        }
        val cleanBase = BASE_URL.trimEnd('/')
        val cleanPath = trimmed.trimStart('/')
        return "$cleanBase/$cleanPath"
    }
}
"""

with open(constants_path, "w", encoding="utf-8") as f:
    f.write(constants_content)
print("Constants.kt written successfully")

# Update ProfileScreen.kt
profile_path = r"C:\Users\ayanm\AndroidStudioProjects\CampusConnectStudent\app\src\main\java\com\campusconnect\student\ui\profile\ProfileScreen.kt"
with open(profile_path, "r", encoding="utf-8") as f:
    profile_content = f.read()

# Add import if needed
if "import com.campusconnect.student.utils.Constants" not in profile_content:
    profile_content = profile_content.replace(
        "import coil.compose.AsyncImage",
        "import coil.compose.AsyncImage\nimport com.campusconnect.student.utils.Constants"
    )

# Replace .data(profile.profilePhoto) with .data(Constants.getFullImageUrl(profile.profilePhoto))
profile_content = profile_content.replace(
    ".data(profile.profilePhoto)",
    ".data(Constants.getFullImageUrl(profile.profilePhoto))"
)

with open(profile_path, "w", encoding="utf-8") as f:
    f.write(profile_content)
print("ProfileScreen.kt updated successfully")

# Update DashboardScreen.kt
dashboard_path = r"C:\Users\ayanm\AndroidStudioProjects\CampusConnectStudent\app\src\main\java\com\campusconnect\student\ui\home\DashboardScreen.kt"
with open(dashboard_path, "r", encoding="utf-8") as f:
    dashboard_content = f.read()

if "import com.campusconnect.student.utils.Constants" not in dashboard_content:
    dashboard_content = dashboard_content.replace(
        "import coil.compose.AsyncImage",
        "import coil.compose.AsyncImage\nimport com.campusconnect.student.utils.Constants"
    )

dashboard_content = dashboard_content.replace(
    ".data(profile?.profilePhoto)",
    ".data(Constants.getFullImageUrl(profile?.profilePhoto))"
)

with open(dashboard_path, "w", encoding="utf-8") as f:
    f.write(dashboard_content)
print("DashboardScreen.kt updated successfully")
