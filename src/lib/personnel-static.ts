// Temporary edition adapter until the verified runtime publisher is deployed.
import snapshot from '../../data/personnel.json';
import collection from '../../data/personnel-collection.json';
import quarterback from '../../data/quarterbacks.json';
import quarterbackCollection from '../../data/quarterback-collection.json';
import participationCollection from '../../data/participation-collection.json';
import history from '../../data/personnel-changes.json';
import historical from '../../data/player-usage.json';
import current from '../../data/season-participation.json';
import type { PersonnelEvidence } from './personnel-evidence';

export const staticPersonnelEvidence: PersonnelEvidence = {
  snapshot, collection, quarterback, quarterbackCollection,
  participationCollection, history, historical, current,
};
