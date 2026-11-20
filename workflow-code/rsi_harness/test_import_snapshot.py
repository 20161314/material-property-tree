import unittest

from import_snapshot import (
    add_inventory_alias_claim,
    component_kind_from_inventory,
    validate_alias_registry,
)


class ComponentKindImportTests(unittest.TestCase):
    def test_explicit_whole_id_remains_whole(self):
        self.assertEqual(component_kind_from_inventory({
            'component_id': 'OBJ-1-WHOLE', 'component_basis': 'source fallback'
        }), 'WHOLE')

    def test_explicit_official_whole_fallback_basis_is_recognized(self):
        self.assertEqual(component_kind_from_inventory({
            'component_id': 'CMP-ABO-1-WHOLE-UNRESOLVED',
            'component_scope': 'whole object; material unresolved',
            'component_basis': 'whole-object fallback from official 3D manifest; authored mesh/part structure not yet inspected'
        }), 'WHOLE')

    def test_scoped_material_region_is_not_mistaken_for_whole_object(self):
        self.assertEqual(component_kind_from_inventory({
            'component_id': 'CMP-ABO-2-WHOLE-UNRESOLVED',
            'component_scope': 'title-identified stoneware body; hardware and inserts excluded',
            'component_basis': 'official listing material field plus official title component corroboration'
        }), 'UNCLASSIFIED')

    def test_source_part_without_representation_proof_stays_unclassified(self):
        self.assertEqual(component_kind_from_inventory({
            'component_id': 'COMP-PHYSXMOB-100013-PART-0000',
            'component_scope': 'Button',
            'component_basis': 'PHYSX_MOBILITY_FINALJSON_PART_RECORD_HUMAN_VERIFIED_RELEASE'
        }), 'UNCLASSIFIED')


class SourceAliasImportTests(unittest.TestCase):
    def test_registry_must_keep_alias_only_source_identity_contract(self):
        validate_alias_registry([
            {'dataset_id': 'SLATPHYS', 'ingestion_status': 'alias_only_do_not_add',
             'deduplication_key': 'Objaverse UID'},
            {'dataset_id': 'NVIDIA-SIMREADY-LEGACY-PACKS',
             'deduplication_key': 'official pack URL plus canonical USD archive path',
             'ingested_unique_objects': '1029'},
        ])
        with self.assertRaisesRegex(ValueError, 'SLATPHYS registry'):
            validate_alias_registry([
                {'dataset_id': 'SLATPHYS', 'ingestion_status': 'additive',
                 'deduplication_key': 'Objaverse UID'},
                {'dataset_id': 'NVIDIA-SIMREADY-LEGACY-PACKS',
                 'deduplication_key': 'official pack URL plus canonical USD archive path',
                 'ingested_unique_objects': '1029'},
            ])

    def test_slat_uid_is_alias_of_pixie_uid_not_additive_identity(self):
        claims = {}
        row = {'object_id': 'OBJ-PIXIE-1', 'required_source_primary': 'PIXIEVERSE',
               'required_source_memberships': 'PIXIEVERSE;SLATPHYS',
               'source_asset_id': '0123456789abcdef0123456789abcdef',
               'source_dataset': 'PIXIEVerse public release'}
        add_inventory_alias_claim(claims, row)
        self.assertEqual(list(claims), [('SLATPHYS', row['source_asset_id'])])
        self.assertEqual(claims[('SLATPHYS', row['source_asset_id'])]['object_id'], 'OBJ-PIXIE-1')
        self.assertEqual(claims[('SLATPHYS', row['source_asset_id'])]['reviewed'], 1)
        with self.assertRaisesRegex(ValueError, 'PIXIEVERSE'):
            add_inventory_alias_claim(claims, {**row, 'required_source_primary': 'ABO-3D'})

    def test_legacy_paths_deduplicate_to_one_reviewed_official_alias(self):
        claims = {}
        base = {'object_id': 'OBJ-GVM-1', 'required_source_primary': 'VOMP-GVM-PUBLIC',
                'required_source_memberships': 'VOMP-GVM-PUBLIC;NVIDIA-SIMREADY-LEGACY-PACKS',
                'asset_package_url': 'https://cdn.example/pack.zip',
                'asset_archive_entry_path': 'Assets/asset.usd'}
        add_inventory_alias_claim(claims, {**base,
            'asset_alias_status': 'OFFICIAL_ZIP_ALIAS_CANONICAL_GVM_OBJECT',
            'asset_alias_source_id': 'NVIDIA-SIMREADY::Pack::asset'})
        add_inventory_alias_claim(claims, {**base,
            'asset_alias_status': 'ALIAS_TO_GVM_CANONICAL_GEOMETRY',
            'asset_alias_source_id': 'OBJ-GVM-1'})
        key = ('NVIDIA-SIMREADY-LEGACY-PACKS', 'https://cdn.example/pack.zip::Assets/asset.usd')
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[key]['object_id'], 'OBJ-GVM-1')
        self.assertEqual(claims[key]['reviewed'], 1)
        self.assertIn('ALIAS_TO_GVM_CANONICAL_GEOMETRY', claims[key]['basis'])

    def test_alias_key_cannot_point_to_two_canonical_objects(self):
        claims = {}
        base = {'object_id': 'OBJ-GVM-1', 'required_source_primary': 'VOMP-GVM-PUBLIC',
                'required_source_memberships': 'VOMP-GVM-PUBLIC;NVIDIA-SIMREADY-LEGACY-PACKS',
                'asset_alias_status': 'OFFICIAL_ZIP_ALIAS_CANONICAL_GVM_OBJECT',
                'asset_alias_source_id': 'NVIDIA-SIMREADY::Pack::asset',
                'asset_package_url': 'https://cdn.example/pack.zip',
                'asset_archive_entry_path': 'Assets/asset.usd'}
        add_inventory_alias_claim(claims, base)
        with self.assertRaisesRegex(ValueError, 'multiple canonical objects'):
            add_inventory_alias_claim(claims, {**base, 'object_id': 'OBJ-GVM-2'})


if __name__ == '__main__':
    unittest.main()
