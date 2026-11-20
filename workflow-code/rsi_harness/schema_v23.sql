-- RSI 2.3 additive runtime schema.
-- Apply after schema.sql in a new shadow database. This file never mutates a
-- released database and contains no automatic admission of facts.
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS scans(
  scan_id TEXT PRIMARY KEY,
  purpose TEXT NOT NULL CHECK(purpose IN('MATERIAL','OBJECT','MIXED')),
  data_epoch TEXT NOT NULL,
  tree_epoch TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN('READY','RUNNING','PAUSED_BUDGET','COMPLETE','CANCELLED')),
  claims_limit INTEGER NOT NULL CHECK(claims_limit>=0),
  seconds_limit REAL NOT NULL CHECK(seconds_limit>=0),
  claims_spent INTEGER NOT NULL DEFAULT 0 CHECK(claims_spent>=0),
  seconds_spent REAL NOT NULL DEFAULT 0 CHECK(seconds_spent>=0),
  budget_revision INTEGER NOT NULL DEFAULT 0 CHECK(budget_revision>=0),
  frontier_json TEXT NOT NULL DEFAULT '[]',
  completed_routes_json TEXT NOT NULL DEFAULT '[]',
  created_at REAL NOT NULL,
  updated_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS scan_routes(
  scan_id TEXT NOT NULL REFERENCES scans(scan_id),
  business_key TEXT NOT NULL,
  lane TEXT NOT NULL CHECK(lane IN('MATERIAL','OBJECT')),
  task_type TEXT NOT NULL,
  subject_id TEXT NOT NULL,
  attribute_scope TEXT NOT NULL,
  priority INTEGER NOT NULL,
  depth INTEGER NOT NULL,
  family TEXT NOT NULL,
  flexible INTEGER NOT NULL DEFAULT 0 CHECK(flexible IN(0,1)),
  route_key TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN('PENDING','LEASED','DONE','COOLDOWN','REJECTED')),
  attempts INTEGER NOT NULL DEFAULT 0 CHECK(attempts>=0),
  last_outcome TEXT NOT NULL DEFAULT '',
  last_error TEXT NOT NULL DEFAULT '',
  retry_at REAL NOT NULL DEFAULT 0,
  lease_token TEXT,
  lease_owner TEXT,
  lease_until REAL,
  first_seen REAL NOT NULL,
  updated_at REAL NOT NULL,
  PRIMARY KEY(scan_id,business_key,route_key)
);
CREATE INDEX IF NOT EXISTS scan_routes_ready
  ON scan_routes(scan_id,lane,status,priority,depth,family,updated_at);

CREATE TABLE IF NOT EXISTS scan_runs(
  run_id TEXT PRIMARY KEY,
  scan_id TEXT NOT NULL REFERENCES scans(scan_id),
  started_at REAL NOT NULL,
  finished_at REAL,
  active INTEGER NOT NULL DEFAULT 1 CHECK(active IN(0,1)),
  max_claims INTEGER NOT NULL CHECK(max_claims>=1),
  claims INTEGER NOT NULL DEFAULT 0 CHECK(claims>=0),
  UNIQUE(run_id,scan_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_run_per_scan ON scan_runs(scan_id) WHERE active=1;

CREATE TABLE IF NOT EXISTS scan_budget_events(
  scan_id TEXT NOT NULL REFERENCES scans(scan_id),
  event_id TEXT NOT NULL,
  event_sha256 TEXT NOT NULL,
  expected_revision INTEGER NOT NULL,
  revision_after INTEGER NOT NULL,
  limits_before_json TEXT NOT NULL,
  limits_after_json TEXT NOT NULL,
  spent_before_json TEXT NOT NULL,
  authorization_scope TEXT NOT NULL,
  actor TEXT NOT NULL,
  reason TEXT NOT NULL,
  created_at REAL NOT NULL,
  PRIMARY KEY(scan_id,event_id),
  UNIQUE(scan_id,event_sha256)
);

CREATE TABLE IF NOT EXISTS proposal_lineage(
  proposal_key TEXT PRIMARY KEY REFERENCES proposals(proposal_key),
  parent_release_id TEXT NOT NULL,
  parent_fact_epoch TEXT NOT NULL,
  parent_data_sha256 TEXT NOT NULL,
  delta_sha256 TEXT NOT NULL,
  merge_status TEXT NOT NULL CHECK(merge_status IN('UNMERGED','MERGED','ROLLED_BACK','REBASED')),
  before_sha256 TEXT,
  after_sha256 TEXT,
  merged_by TEXT,
  merged_at REAL,
  receipt_json TEXT NOT NULL DEFAULT '{}',
  CHECK((merge_status='MERGED') = (after_sha256 IS NOT NULL AND merged_by IS NOT NULL AND merged_at IS NOT NULL))
);

CREATE TABLE IF NOT EXISTS review_history(
  review_id TEXT PRIMARY KEY,
  proposal_key TEXT NOT NULL REFERENCES proposals(proposal_key),
  manifest_sha256 TEXT NOT NULL,
  reviewer TEXT NOT NULL,
  decision TEXT NOT NULL CHECK(decision IN('PASS','HOLD','REJECT')),
  basis TEXT NOT NULL,
  created_at REAL NOT NULL,
  UNIQUE(review_id,manifest_sha256)
);
CREATE INDEX IF NOT EXISTS review_history_lookup
  ON review_history(proposal_key,manifest_sha256,created_at);
CREATE TRIGGER IF NOT EXISTS review_history_no_update
BEFORE UPDATE ON review_history BEGIN SELECT RAISE(ABORT,'review history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS review_history_no_delete
BEFORE DELETE ON review_history BEGIN SELECT RAISE(ABORT,'review history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS scan_budget_events_no_update
BEFORE UPDATE ON scan_budget_events BEGIN SELECT RAISE(ABORT,'scan budget events are append-only'); END;
CREATE TRIGGER IF NOT EXISTS scan_budget_events_no_delete
BEFORE DELETE ON scan_budget_events BEGIN SELECT RAISE(ABORT,'scan budget events are append-only'); END;
CREATE TRIGGER IF NOT EXISTS events_no_update
BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT,'execution events are append-only'); END;
CREATE TRIGGER IF NOT EXISTS events_no_delete
BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT,'execution events are append-only'); END;

CREATE TABLE IF NOT EXISTS object_configurations(
  configuration_key TEXT PRIMARY KEY,
  object_id TEXT NOT NULL REFERENCES objects(id),
  geometry_key TEXT NOT NULL,
  config_signature TEXT NOT NULL,
  accepted INTEGER NOT NULL DEFAULT 0 CHECK(accepted IN(0,1)),
  basis TEXT NOT NULL,
  raw_json TEXT NOT NULL DEFAULT '{}',
  UNIQUE(geometry_key,config_signature)
);

CREATE TABLE IF NOT EXISTS object_delivery_audits(
  object_id TEXT PRIMARY KEY REFERENCES objects(id),
  release_id TEXT NOT NULL,
  geometry_id TEXT NOT NULL,
  dedup_reviewed INTEGER NOT NULL CHECK(dedup_reviewed IN(0,1)),
  source_link_verified INTEGER NOT NULL CHECK(source_link_verified IN(0,1)),
  asset_location_verified INTEGER NOT NULL CHECK(asset_location_verified IN(0,1)),
  asset_member_locator TEXT NOT NULL,
  license_status TEXT NOT NULL,
  access_status TEXT NOT NULL,
  review_status TEXT NOT NULL CHECK(review_status IN('PASS','HOLD','REJECT')),
  review_basis TEXT NOT NULL,
  raw_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS object_scope_audits(
  object_id TEXT PRIMARY KEY REFERENCES objects(id),
  source_scope_complete INTEGER NOT NULL CHECK(source_scope_complete IN(0,1)),
  component_readiness_basis TEXT NOT NULL,
  whole_scope_positive INTEGER CHECK(whole_scope_positive IN(0,1) OR whole_scope_positive IS NULL),
  source_locator TEXT NOT NULL,
  review_status TEXT NOT NULL CHECK(review_status IN('PASS','HOLD','REJECT')),
  raw_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS object_geometry_groups(
  geometry_id TEXT PRIMARY KEY,
  reviewed INTEGER NOT NULL CHECK(reviewed IN(0,1)),
  canonical_object_id TEXT NOT NULL REFERENCES objects(id),
  comparison_method TEXT NOT NULL,
  basis TEXT NOT NULL,
  raw_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS release_views(
  release_id TEXT NOT NULL,
  view_name TEXT NOT NULL CHECK(view_name IN('overview','material_tree','evidence_matrix')),
  input_sha256 TEXT NOT NULL,
  output_sha256 TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN('BUILT','VERIFIED','FAILED')),
  created_at REAL NOT NULL,
  PRIMARY KEY(release_id,view_name)
);
CREATE TRIGGER IF NOT EXISTS release_views_identity_immutable
BEFORE UPDATE ON release_views
WHEN OLD.status<>'BUILT'
  OR NEW.release_id<>OLD.release_id
  OR NEW.view_name<>OLD.view_name
  OR NEW.input_sha256<>OLD.input_sha256
  OR NEW.output_sha256<>OLD.output_sha256
  OR NEW.status NOT IN('VERIFIED','FAILED')
BEGIN SELECT RAISE(ABORT,'release view build is frozen'); END;
CREATE TRIGGER IF NOT EXISTS release_views_no_delete
BEFORE DELETE ON release_views BEGIN SELECT RAISE(ABORT,'release view history is append-only'); END;
