import importlib
import importlib.machinery
import importlib.util
import sys
from pathlib import Path


def load_local_settings():
    """Load `jaston/settings.py` directly to avoid importing package `jaston` (which initializes Celery)."""
    backend_root = Path(__file__).resolve().parents[1]
    # Ensure backend root is on sys.path so `apps` and `config` packages import correctly
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))
    settings_path = backend_root / 'jaston' / 'settings.py'
    loader = importlib.machinery.SourceFileLoader('local_jaston_settings', str(settings_path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def resolve_task_name(name: str):
    """Attempt to import the module and resolve the attribute for a task name like 'apps.core.tasks.cleanup_soft_deleted_records'."""
    if not name or not isinstance(name, str):
        return False
    parts = name.rsplit('.', 1)
    if len(parts) != 2:
        return False
    module_name, attr = parts
    try:
        mod = importlib.import_module(module_name)
        return hasattr(mod, attr)
    except Exception:
        # Fall back to static analysis: locate module file and parse AST for the attribute name
        try:
            backend_root = Path(__file__).resolve().parents[1]
            module_path = backend_root / Path(module_name.replace('.', '/')).with_suffix('.py')
            if not module_path.exists():
                return False
            import ast
            with open(module_path, 'r', encoding='utf-8') as f:
                node = ast.parse(f.read(), filename=str(module_path))
            for child in node.body:
                # function definitions
                if isinstance(child, ast.FunctionDef) and child.name == attr:
                    return True
                # assignments like `task = shared_task(...)` (unlikely here), check targets
                if isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(target, ast.Name) and target.id == attr:
                            return True
            return False
        except Exception:
            return False


def test_celery_task_routes_resolvable():
    settings = load_local_settings()
    routes = getattr(settings, 'CELERY_TASK_ROUTES', {}) or {}
    assert isinstance(routes, dict)
    for task_name in routes.keys():
        assert resolve_task_name(task_name), f"Task route '{task_name}' is not importable or attribute missing"


def test_celery_beat_schedule_tasks_resolvable():
    settings = load_local_settings()
    cfg = getattr(settings, 'CELERY_CONFIG', {}) or {}
    beat = cfg.get('beat_schedule', {})
    assert isinstance(beat, dict)
    for entry in beat.values():
        task_name = entry.get('task')
        assert resolve_task_name(task_name), f"Beat task '{task_name}' is not importable or attribute missing"
