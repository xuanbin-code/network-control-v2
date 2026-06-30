"""数据库初始化脚本"""


def _default_lan_subnets():
    return '["192.168.1.0/24"]'


INIT_SQL = f"""
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS machines (
    ip TEXT PRIMARY KEY,
    hostname TEXT DEFAULT '',
    mac TEXT,
    mode TEXT DEFAULT 'disconnect',
    online INTEGER DEFAULT 0,
    last_heartbeat REAL
);

CREATE TABLE IF NOT EXISTS whitelist_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL UNIQUE,
    enabled INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS blacklist_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL UNIQUE,
    enabled INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS browsing_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL,
    domain TEXT NOT NULL,
    ts REAL NOT NULL
);

INSERT OR IGNORE INTO settings (key, value) VALUES ('ws_port', '8765');
INSERT OR IGNORE INTO settings (key, value) VALUES ('api_port', '8770');
INSERT OR IGNORE INTO settings (key, value) VALUES ('heartbeat_interval', '20');
INSERT OR IGNORE INTO settings (key, value) VALUES ('heartbeat_timeout', '60');
INSERT OR IGNORE INTO settings (key, value) VALUES ('lan_subnets', '{_default_lan_subnets()}');
INSERT OR IGNORE INTO settings (key, value) VALUES ('upstream_dns', '114.114.114.114');
INSERT OR IGNORE INTO settings (key, value) VALUES ('filter_mode', 'whitelist');
INSERT OR IGNORE INTO settings (key, value) VALUES ('tray_password_hash', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9');
INSERT OR IGNORE INTO settings (key, value) VALUES ('unlock_password_hash', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9');
"""
