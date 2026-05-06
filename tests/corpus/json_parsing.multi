# JSON Parsing Project
# WASM Corpus Projects
# English variant
#
# Demonstrates:
# - JSON parsing (string processing)
# - JSON stringification (serialization)
# - Data structure manipulation
# - Data-intensive operations ideal for WASM

# SPDX-License-Identifier: GPL-3.0-or-later

def parse_json_simple(json_str: string) -> objet:
    """Parse simple JSON (using built-in parser)."""
    import json
    retourne json.loads(json_str)


def stringify_json(obj: objet) -> string:
    """Convert object to JSON string."""
    import json
    retourne json.dumps(obj)


def create_sample_data() -> objet:
    """Create sample data structure."""
    data = {
        "users": [
            {
                "id": 1,
                "name": "Alice",
                "email": "alice@example.com",
                "roles": ["admin", "user"],
            },
            {
                "id": 2,
                "name": "Bob",
                "email": "bob@example.com",
                "roles": ["user"],
            },
            {
                "id": 3,
                "name": "Charlie",
                "email": "charlie@example.com",
                "roles": ["user", "moderator"],
            },
        ],
        "metadata": {
            "version": "1.0",
            "timestamp": "2024-02-22T10:00:00Z",
            "total_users": 3,
        },
    }
    retourne data


def filter_users_by_role(users: list, role: string) -> list:
    """Filter users that have a specific role."""
    filtered = []
    pour user dans users:
        si "roles" dans user:
            si role dans user["roles"]:
                filtered.ajouter(user)
    retourne filtered


def count_users_by_role(users: list) -> objet:
    """Count occurrences of each role."""
    role_counts = {}
    pour user dans users:
        si "roles" dans user:
            pour role dans user["roles"]:
                si role not dans role_counts:
                    role_counts[role] = 0
                role_counts[role] = role_counts[role] + 1
    retourne role_counts


def extract_emails(users: list) -> list:
    """Extract email addresses from user list."""
    emails = []
    pour user dans users:
        si "email" dans user:
            emails.ajouter(user["email"])
    retourne emails


def transform_user_names(users: list) -> list:
    """Transform user names to uppercase."""
    transformed = []
    pour user dans users:
        user_copy = {
            "id": user.get("id"),
            "name": user.get("name", "").upper(),
            "email": user.get("email"),
        }
        transformed.ajouter(user_copy)
    retourne transformed


def merge_json_objects(obj1: objet, obj2: objet) -> objet:
    """Merge two JSON objects."""
    merged = obj1.copy()
    pour key, value dans obj2.items():
        merged[key] = value
    retourne merged


def validate_user(user: objet) -> booleen:
    """Validate user object has required fields."""
    required_fields = ["id", "name", "email"]
    pour field dans required_fields:
        si field not dans user:
            retourne false
    retourne true


def main():
    afficher("=== JSON Parsing Demonstration ===")

    # Create and serialize sample data
    afficher("\n1. Creating sample data...")
    data = create_sample_data()
    afficher(f"Created data structure with {longueur(data['users'])} users")

    # Convert to JSON
    afficher("\n2. Serializing to JSON...")
    json_string = stringify_json(data)
    afficher(f"JSON string length: {longueur(json_string)} characters")
    afficher(f"First 100 chars: {json_string[0:100]}")

    # Parse back from JSON
    afficher("\n3. Parsing JSON back to object...")
    parsed_data = parse_json_simple(json_string)
    afficher(f"Parsed successfully: {longueur(parsed_data['users'])} users")

    # Filter operations
    afficher("\n4. Filtering users by role...")
    admin_users = filter_users_by_role(data["users"], "admin")
    afficher(f"Found {longueur(admin_users)} admin user(s)")

    moderator_users = filter_users_by_role(data["users"], "moderator")
    afficher(f"Found {longueur(moderator_users)} moderator user(s)")

    # Count roles
    afficher("\n5. Counting roles...")
    role_counts = count_users_by_role(data["users"])
    afficher(f"Role distribution: {role_counts}")

    # Extract emails
    afficher("\n6. Extracting emails...")
    emails = extract_emails(data["users"])
    afficher(f"Emails: {emails}")

    # Transform data
    afficher("\n7. Transforming user names to uppercase...")
    uppercase_users = transform_user_names(data["users"])
    pour user dans uppercase_users:
        afficher(f"  {user['name']} ({user['email']})")

    # Validate users
    afficher("\n8. Validating users...")
    valid_count = 0
    pour user dans data["users"]:
        si validate_user(user):
            valid_count = valid_count + 1
    afficher(f"Valid users: {valid_count}/{longueur(data['users'])}")

    # Merge objects
    afficher("\n9. Merging JSON objects...")
    new_metadata = {"author": "test", "revision": 2}
    merged = merge_json_objects(data["metadata"], new_metadata)
    afficher(f"Merged metadata keys: {longueur(merged)}")

    # Stress test: large JSON
    afficher("\n10. Stress test: processing large JSON...")
    large_data = {
        "items": [],
    }
    pour i dans intervalle(100):
        large_data["items"].ajouter({
            "id": i,
            "value": i * 10,
            "processed": false,
        })

    large_json = stringify_json(large_data)
    afficher(f"Large JSON created: {longueur(large_json)} characters")

    parsed_large = parse_json_simple(large_json)
    afficher(f"Parsed large JSON: {longueur(parsed_large['items'])} items")

    afficher("\n✓ All JSON operations completed successfully")


main()
