# Alembic Migrations Guide for FastAPI + SQLModel

This guide shows how to use Alembic for database migrations in your FastAPI/SQLModel project.

## 🚀 Quick Start

### 1. Create a New Migration

```bash
# Auto-generate migration from model changes
make migrate-create MSG="Add new column to user table"
```

### 2. Apply Migrations

```bash
# Apply all pending migrations
make migrate-upgrade
```

### 3. Check Migration Status

```bash
# Show current revision
make migrate-status

# Show migration history
make migrate-history
```

## 📋 Common Workflows

### Adding a New Model

1. Create your SQLModel class in `src/api/v1/models/`
2. Import it in `migrations/env.py` (if not already imported)
3. Generate migration: `make migrate-create MSG="Add new model"`
4. Review the generated migration file
5. Apply migration: `make migrate-upgrade`

### Modifying an Existing Model

1. Update your SQLModel class
2. Generate migration: `make migrate-create MSG="Update model fields"`
3. Review and edit the migration if needed
4. Apply migration: `make migrate-upgrade`

### Adding Indexes or Constraints

```python
# In your model
class User(SQLModel, table=True):
    email: str = Field(index=True)  # Alembic will detect this
    username: str = Field(unique=True)  # And this
```

## 🔧 Configuration

### Database URL

The database URL is configured in:
- `alembic.ini` - for Alembic commands
- `src/core/config.py` - for your FastAPI app

Make sure both use the same database!

### Environment Variables

You can use environment variables in `alembic.ini`:

```ini
# In alembic.ini
sqlalchemy.url = %(DATABASE_URL)s
```

Then set `DATABASE_URL` environment variable.

## 📁 Project Structure

```
fastapi-starter/
├── migrations/           # Alembic migrations
│   ├── versions/        # Migration files
│   ├── env.py          # Alembic environment
│   └── script.py.mako  # Template for new migrations
├── src/
│   └── api/v1/models/  # Your SQLModel classes
│       ├── user.py
│       ├── workspace.py
│       └── workspace_member.py
└── alembic.ini         # Alembic configuration
```

## 🛠️ Best Practices

### 1. Always Review Generated Migrations

Auto-generated migrations are not always perfect. Always review:
- Check column types are correct
- Verify foreign key constraints
- Ensure indexes are properly created
- Add data migration logic if needed

### 2. Test Migrations

```bash
# Apply migration
make migrate-upgrade

# Test your app
make dev-server
```

### 3. Name Migrations Descriptively

```bash
# Good ✅
make migrate-create MSG="Add user profile fields and indexes"

# Bad ❌
make migrate-create MSG="Update stuff"
```

### 4. Use the Makefile

Use the provided `make` commands to manage migrations.

## 🔄 Data Migrations

For complex data transformations, edit the migration file manually:

```python
def upgrade() -> None:
    # Schema changes first
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))

    # Data migration
    connection = op.get_bind()
    connection.execute(
        text("UPDATE users SET full_name = first_name || ' ' || last_name")
    )

    # Make column non-nullable after data migration
    op.alter_column('users', 'full_name', nullable=False)
```

## 🚨 Troubleshooting

### Migration File is Empty

If `--autogenerate` creates an empty migration:
1. Ensure all models are imported in `migrations/env.py`
2. Check that models have `table=True`
3. Verify database URL in `alembic.ini`

### Foreign Key Errors

Make sure foreign key relationships are properly defined:

```python
class WorkspaceMember(SQLModel, table=True):
    user_id: UUID = Field(foreign_key="users.id")
    workspace_id: UUID = Field(foreign_key="workspaces.id")
```

### Rollback Fails

If rollback fails, you may need to:
1. Fix the downgrade function in the migration
2. Or create a new migration to fix the issue
3. Never edit applied migrations in production!

## 📚 Advanced Usage

### Multiple Database Support

For multiple databases, you can create separate Alembic configurations or use Alembic's multi-database support.

### Production Deployment

```bash
# In your deployment script
make migrate-upgrade
make dev-server
```

Consider using tools like `alembic-offline` for zero-downtime deployments.

## 🎯 Quick Reference

| Command | Description |
|---------|-------------|
| `make migrate-create MSG="message"` | Create new migration |
| `make migrate-upgrade` | Apply all migrations |
| `make migrate-rollback` | Rollback one migration |
| `make migrate-status` | Show current revision |
| `make migrate-history` | Show migration history |

For more details, see the [official Alembic documentation](https://alembic.sqlalchemy.org/).
