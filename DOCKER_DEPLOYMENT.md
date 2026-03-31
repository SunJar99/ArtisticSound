# ArtisticSound - Docker Deployment Guide

## Prerequisites
- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)
- Git for cloning/version control

## Quick Start

### 1. Environment Configuration
The `.env` file contains all configuration. Review and update if needed:
```bash
cd ArtisticSound
cat .env  # Review configuration
```

Key variables:
- `DB_PASSWORD`: PostgreSQL password (change in production!)
- `SECRET_KEY`: Django secret key (change in production!)
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Add your domain/IP addresses

### 2. Start the Application
```bash
# Start PostgreSQL and Django containers in background
docker-compose up -d

# Watch logs in real-time
docker-compose logs -f web

# Or just PostgreSQL logs:
docker-compose logs -f db
```

### 3. Run Database Migrations
Once containers are running:
```bash
# Apply Django migrations
docker-compose exec web python manage.py migrate

# Create superuser (admin account)
docker-compose exec web python manage.py createsuperuser

# Collect static files (for WhiteNoise)
docker-compose exec web python manage.py collectstatic --noreload
```

### 4. Access the Application
- **Website**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

## Common Commands

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f          # All services
docker-compose logs -f web      # Django app only
docker-compose logs -f db       # PostgreSQL only

# Execute commands in container
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py dbshell
docker-compose exec db psql -U artisticsound_user -d artisticsound

# Stop all containers
docker-compose stop

# Stop and remove (preserves data via volumes)
docker-compose down

# Stop and remove including volumes (⚠️ DELETES DATABASE)
docker-compose down -v

# Restart services
docker-compose restart

# View database persistence
docker volume ls
docker volume inspect artisticsound_postgres_data
```

## Data Persistence

Database data is stored in a Docker volume named `artisticsound_postgres_data`. This means:
- ✅ Data persists after `docker-compose down` or restart
- ✅ Can be backed up with `docker volume inspect` commands
- ❌ Only deleted if you run `docker-compose down -v`

## Production Deployment

### Before Going Live:
1. **Generate a new SECRET_KEY** in `.env`
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

2. **Set DEBUG=False**
   ```
   DEBUG=False
   ```

3. **Configure ALLOWED_HOSTS** with your domain
   ```
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

4. **Change database password**
   ```
   DB_PASSWORD=your-secure-password-here
   ```

5. **Use environment-specific .env file**
   - Create `.env.production` with production secrets
   - Link or copy to `.env` when deploying

### Optional: Expose Database Externally
In `docker-compose.yml`, uncomment the `ports` section in the `db` service to enable external access:
```yaml
db:
  ports:
    - "5432:5432"  # Enable if you need external database access
```

### Optional: Add SSL/HTTPS
Update Nginx/reverse proxy configuration to handle SSL certificates. Docker Compose example would need an Nginx container added.

## Troubleshooting

### Database Connection Refused
```bash
# Check if db service is healthy
docker-compose ps

# Check health status
docker inspect $(docker-compose ps -q db)

# Restart database service
docker-compose restart db
```

### Static Files Not Loading
```bash
# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Collect static files again
docker-compose exec web python manage.py collectstatic --noreload
```

### Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
# Kill the process or change port in docker-compose.yml
```

### View Django Errors
```bash
# Get application logs with full traceback
docker-compose logs web

# Get last 100 lines
docker-compose logs --tail=100 web
```

## Security Checklist

- [ ] Change `SECRET_KEY` in `.env` to a unique value
- [ ] Set `DEBUG=False` before production
- [ ] Update `ALLOWED_HOSTS` with actual domain
- [ ] Change `DB_PASSWORD` to something secure
- [ ] Don't commit `.env` file to version control (add to `.gitignore`)
- [ ] Set up proper SSL/TLS certificates
- [ ] Configure firewall rules (only expose ports 80/443)
- [ ] Set up regular database backups
- [ ] Configure monitoring and logging

## Backup and Restore

### Backup Database
```bash
# Create a backup file
docker-compose exec db pg_dump -U artisticsound_user -d artisticsound > backup.sql

# Or use volume backup
docker run --rm -v artisticsound_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/db-backup.tar.gz /data
```

### Restore Database
```bash
# Restore from backup
docker-compose exec -T db psql -U artisticsound_user -d artisticsound < backup.sql
```

## Upgrading Django or Dependencies

1. Update `requirements.txt` with new package versions
2. Rebuild the image: `docker-compose build --no-cache`
3. Restart services: `docker-compose down && docker-compose up -d`
4. Run migrations: `docker-compose exec web python manage.py migrate`

## Next Steps

1. ✅ Save this guide for reference
2. ✅ Test locally with `docker-compose up -d`
3. ✅ Verify database is working: `docker-compose exec db psql -U artisticsound_user -d artisticsound`
4. ✅ Run migrations and create superuser
5. ✅ Test application at http://localhost:8000
6. ✅ Deploy to your hosting provider
7. ✅ Set up monitoring and backups