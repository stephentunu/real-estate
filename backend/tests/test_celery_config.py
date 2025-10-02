from config.celery_config import get_celery_config


def test_get_celery_config_basics():
    cfg = get_celery_config()
    assert isinstance(cfg, dict), 'get_celery_config must return a dict'
    assert 'broker_url' in cfg, 'broker_url must be configured in the returned celery config'
    assert cfg.get('broker_url'), 'broker_url must not be empty'
