# Define the directories
BACKEND_DIR=backend
FRONTEND_DIR=frontend

# Define the commands
.PHONY: start backend frontend stop

start:
	@echo "Starting both backend and frontend..."
	@$(MAKE) -j2 backend frontend

backend:
	@echo "Starting Django backend..."
	@cd $(BACKEND_DIR) && python manage.py runserver

frontend:
	@echo "Starting Vite frontend..."
	@cd $(FRONTEND_DIR) && npm run dev

stop:
	@echo "Stopping both backend and frontend..."
	@pkill -f 'python manage.py runserver' || true
	@pkill -f 'npm run dev' || true
	@echo "Stopped all processes."