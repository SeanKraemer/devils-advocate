test-backend:
	pytest -q

test-frontend:
	cd frontend && npm test

lint-frontend:
	cd frontend && npm run lint

build-frontend:
	cd frontend && npm run build

test:
	make test-backend && make test-frontend

clean:
	rm -rf frontend/dist .pytest_cache backend/__pycache__ backend/rag/__pycache__ tests/backend/__pycache__
