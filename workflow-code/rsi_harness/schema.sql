PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS fact_revision(id INTEGER PRIMARY KEY CHECK(id=1),generation INTEGER NOT NULL);
INSERT OR IGNORE INTO fact_revision VALUES(1,0);
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS raw_source_rows(
 input_path TEXT NOT NULL,row_number INTEGER NOT NULL,payload_zlib BLOB NOT NULL,
 PRIMARY KEY(input_path,row_number));
CREATE TABLE IF NOT EXISTS nodes(
 id TEXT PRIMARY KEY,name_cn TEXT NOT NULL,name_en TEXT NOT NULL,
 kind TEXT NOT NULL CHECK(kind IN('MATERIAL','CATEGORY','SPECIAL','EXCLUDED')),
 granularity TEXT NOT NULL DEFAULT 'SOURCE_DEFINED',identity_basis TEXT NOT NULL DEFAULT '',
 family TEXT NOT NULL DEFAULT 'unclassified',flexible INTEGER NOT NULL DEFAULT 0,
 active INTEGER NOT NULL DEFAULT 1,raw_json TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS edges(
 parent_id TEXT NOT NULL REFERENCES nodes,child_id TEXT NOT NULL REFERENCES nodes,
 kind TEXT NOT NULL CHECK(kind IN('IS_A','DISPLAY','PART_OF','CONSTITUENT_OF','COATING_OF','SIMILAR_TO')),
 accepted INTEGER NOT NULL DEFAULT 0,object_up INTEGER NOT NULL DEFAULT 0,property_up INTEGER NOT NULL DEFAULT 0,
 basis TEXT NOT NULL,raw_json TEXT NOT NULL DEFAULT '{}',PRIMARY KEY(parent_id,child_id,kind),
 CHECK(parent_id<>child_id),CHECK((object_up=0 AND property_up=0) OR (kind='IS_A' AND accepted=1)));
CREATE TABLE IF NOT EXISTS objects(
 id TEXT PRIMARY KEY,namespace TEXT NOT NULL,source_uid TEXT NOT NULL,name_cn TEXT NOT NULL,name_en TEXT NOT NULL,
 source_url TEXT NOT NULL,asset_url TEXT NOT NULL,geometry_sha256 TEXT,accepted INTEGER NOT NULL DEFAULT 1,
 raw_json TEXT NOT NULL DEFAULT '{}',UNIQUE(namespace,source_uid));
CREATE TABLE IF NOT EXISTS object_aliases(
 namespace TEXT NOT NULL,source_uid TEXT NOT NULL,object_id TEXT NOT NULL REFERENCES objects,
 basis TEXT NOT NULL,reviewed INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(namespace,source_uid));
CREATE TABLE IF NOT EXISTS components(
 object_id TEXT NOT NULL REFERENCES objects,id TEXT NOT NULL,
 kind TEXT NOT NULL CHECK(kind IN('PHYSICAL','SEMANTIC','WHOLE','UNCLASSIFIED')),
 scope TEXT NOT NULL,basis TEXT NOT NULL,raw_json TEXT NOT NULL DEFAULT '{}',PRIMARY KEY(object_id,id));
CREATE TABLE IF NOT EXISTS material_links(
 id TEXT PRIMARY KEY,object_id TEXT NOT NULL,component_id TEXT NOT NULL,material_id TEXT NOT NULL REFERENCES nodes,
 scope TEXT NOT NULL,mode TEXT NOT NULL,option_group TEXT NOT NULL DEFAULT '',accepted INTEGER NOT NULL,
 basis TEXT NOT NULL,raw_json TEXT NOT NULL DEFAULT '{}',FOREIGN KEY(object_id,component_id) REFERENCES components(object_id,id));
CREATE INDEX IF NOT EXISTS links_material ON material_links(material_id,accepted);
CREATE TABLE IF NOT EXISTS documents(
 id TEXT PRIMARY KEY,lineage_key TEXT,lineage_verified INTEGER NOT NULL DEFAULT 0,
 url TEXT NOT NULL DEFAULT '',raw_json TEXT NOT NULL DEFAULT '{}',CHECK(lineage_verified=0 OR lineage_key IS NOT NULL));
CREATE TABLE IF NOT EXISTS evidence_groups(
 id TEXT PRIMARY KEY,document_id TEXT NOT NULL REFERENCES documents,source_material TEXT NOT NULL,
 source_group_key TEXT NOT NULL,accepted INTEGER NOT NULL DEFAULT 1,provenance TEXT NOT NULL,
 raw_json TEXT NOT NULL DEFAULT '{}',UNIQUE(document_id,source_group_key));
CREATE TABLE IF NOT EXISTS observations(
 group_id TEXT NOT NULL REFERENCES evidence_groups,property TEXT NOT NULL CHECK(property IN('E','nu','rho')),
 low REAL NOT NULL,high REAL NOT NULL,unit TEXT NOT NULL,accepted INTEGER NOT NULL DEFAULT 1,
 raw_json TEXT NOT NULL DEFAULT '{}',PRIMARY KEY(group_id,property),CHECK(low<=high));
CREATE TABLE IF NOT EXISTS group_material_refs(
 group_id TEXT NOT NULL REFERENCES evidence_groups,material_id TEXT NOT NULL REFERENCES nodes,
 relation TEXT NOT NULL CHECK(relation IN('DIRECT','REVIEWED_TARGET_SUBTYPE_REFERENCE','REVIEWED_TRUE_CONTAINMENT','FAMILY_ONLY')),
 accepted INTEGER NOT NULL,raw_json TEXT NOT NULL DEFAULT '{}',PRIMARY KEY(group_id,material_id,relation));
CREATE TABLE IF NOT EXISTS material_state(
 material_id TEXT PRIMARY KEY REFERENCES nodes,state INTEGER NOT NULL CHECK(state BETWEEN 1 AND 4),
 depth INTEGER NOT NULL,direct_objects INTEGER NOT NULL,effective_objects INTEGER NOT NULL,
 missing_json TEXT NOT NULL,stats_json TEXT NOT NULL,epoch TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS obligations(
 id TEXT PRIMARY KEY,object_id TEXT REFERENCES objects,component_id TEXT,kind TEXT NOT NULL,
 reason TEXT NOT NULL,resolved INTEGER NOT NULL DEFAULT 0,raw_json TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS runs(
 id TEXT PRIMARY KEY,started REAL NOT NULL,deadline REAL NOT NULL,max_claims INTEGER NOT NULL,
 claims INTEGER NOT NULL DEFAULT 0,per_material INTEGER NOT NULL DEFAULT 3,object_slot INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS run_members(
 run_id TEXT NOT NULL REFERENCES runs,subject_id TEXT NOT NULL,PRIMARY KEY(run_id,subject_id));
CREATE TABLE IF NOT EXISTS tasks(
 id TEXT PRIMARY KEY,business_key TEXT NOT NULL,lane TEXT NOT NULL CHECK(lane IN('MATERIAL','OBJECT')),
 subject_id TEXT NOT NULL,task_type TEXT NOT NULL,tier INTEGER NOT NULL,depth INTEGER NOT NULL,
 epoch TEXT NOT NULL,status TEXT NOT NULL CHECK(status IN('PENDING','LEASED','DONE','COOLDOWN','STALE')),
 created REAL NOT NULL,retry_at REAL NOT NULL DEFAULT 0,owner TEXT,token TEXT,lease_until REAL,
 attempts INTEGER NOT NULL DEFAULT 0,result_json TEXT,UNIQUE(business_key,epoch));
CREATE INDEX IF NOT EXISTS tasks_ready ON tasks(lane,epoch,status,retry_at);
CREATE UNIQUE INDEX IF NOT EXISTS one_business_lease ON tasks(business_key) WHERE status='LEASED';
CREATE TABLE IF NOT EXISTS attempts(
 token TEXT PRIMARY KEY,task_id TEXT NOT NULL REFERENCES tasks,run_id TEXT NOT NULL REFERENCES runs,
 subject_id TEXT NOT NULL,family TEXT NOT NULL,started REAL NOT NULL,finished REAL,outcome TEXT,result_json TEXT);
CREATE TABLE IF NOT EXISTS task_routes(
 business_key TEXT NOT NULL,epoch TEXT NOT NULL,route_key TEXT NOT NULL,token TEXT NOT NULL REFERENCES attempts,
 PRIMARY KEY(business_key,epoch,route_key));
CREATE TABLE IF NOT EXISTS proposals(
 proposal_key TEXT PRIMARY KEY,manifest_sha256 TEXT NOT NULL,collector TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'CANDIDATE');
CREATE TABLE IF NOT EXISTS reviews(
 id TEXT PRIMARY KEY,proposal_key TEXT NOT NULL REFERENCES proposals,manifest_sha256 TEXT NOT NULL,
 reviewer TEXT NOT NULL,decision TEXT NOT NULL CHECK(decision IN('PASS','HOLD','REJECT')),basis TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events(
 id INTEGER PRIMARY KEY AUTOINCREMENT,created REAL NOT NULL,kind TEXT NOT NULL,payload_json TEXT NOT NULL);
