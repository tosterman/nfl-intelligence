import type { PersonnelSnapshot } from './personnel';
import type { QuarterbackSnapshot } from './quarterbacks';
import type { PersonnelChanges } from './personnel-changes';

export type PersonnelEvidence = {
  snapshot: PersonnelSnapshot;
  collection: { status: string; checkedAt?: string };
  quarterback: QuarterbackSnapshot;
  quarterbackCollection: { status: string; checkedAt?: string };
  participationCollection: { status: string; checkedAt?: string };
  history: PersonnelChanges;
  historical: unknown;
  current: unknown;
};
