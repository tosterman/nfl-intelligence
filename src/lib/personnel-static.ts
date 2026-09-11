// Retained edition fixture for archive and component verification.
import snapshot from '../../data/personnel.json';
import collection from '../../data/personnel-collection.json';
import quarterback from '../../data/quarterbacks.json';
import quarterbackCollection from '../../data/quarterback-collection.json';
import participationCollection from '../../data/participation-collection.json';
import history from '../../data/personnel-changes.json';
import historical from '../../data/player-usage.json';
import current from '../../data/season-participation.json';
import type { PersonnelEvidence } from './personnel-evidence';
import type { PersonnelChange } from './personnel-changes';

export const staticPersonnelEvidence: PersonnelEvidence = {
  snapshot, collection, quarterback, quarterbackCollection,
  participationCollection,
  // JSON imports infer absent keys as optional undefined properties across
  // heterogeneous rows. Copy the present keys into the declared dictionary.
  history: {...history, changes: history.changes.map((change: Omit<PersonnelChange, 'fields'> & {fields: Partial<PersonnelChange['fields']>}) => {
    const fields: PersonnelEvidence['history']['changes'][number]['fields'] = {};
    for (const [name, value] of Object.entries(change.fields)) {
      if (value !== undefined) fields[name] = value;
    }
    return {...change, fields};
  })},
  historical, current,
};
