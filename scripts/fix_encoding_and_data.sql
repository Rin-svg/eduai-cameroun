-- ============================================================
-- EDUAI Cameroun — Fix encodage UTF-8 + données de démonstration
-- Exécuter : mysql -u root -p eduai_cameroun < scripts/fix_encoding_and_data.sql
-- ============================================================

-- 1. Forcer l'encodage de la connexion
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 2. Corriger l'encodage des tables concernées
ALTER TABLE epreuves_matiere CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE epreuves_niveau CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE quiz_quiz CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE quiz_question CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE quiz_choix CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 3. Corriger les noms de matières mal encodés
UPDATE epreuves_matiere SET nom = 'Mathématiques'    WHERE code = 'MATH';
UPDATE epreuves_matiere SET nom = 'Français'         WHERE code = 'FR';
UPDATE epreuves_matiere SET nom = 'Physique-Chimie'  WHERE code = 'PC';
UPDATE epreuves_matiere SET nom = 'SVT'              WHERE code = 'SVT';
UPDATE epreuves_matiere SET nom = 'Histoire-Géographie' WHERE code = 'HG';
UPDATE epreuves_matiere SET nom = 'Philosophie'      WHERE code = 'PHILO';
UPDATE epreuves_matiere SET nom = 'Informatique'     WHERE code = 'INFO';
UPDATE epreuves_matiere SET nom = 'Anglais'          WHERE code = 'ANG';
UPDATE epreuves_matiere SET nom = 'Économie'         WHERE code = 'ECO';

-- 4. Corriger les titres/descriptions de quiz mal encodés
UPDATE quiz_quiz SET
    titre = 'Quiz Mathématiques — Terminale',
    description = 'Quiz de révision sur les fonctions dérivées et intégrales.'
WHERE titre LIKE '%Math%' AND titre LIKE '%Terminale%';

-- 5. Corriger les énoncés de questions mal encodés
UPDATE quiz_question SET enonce = 'Quelle est la dérivée de f(x) = x² + 3x + 2 ?'
WHERE enonce LIKE '%d%riv%' OR enonce LIKE '%rive%';

UPDATE quiz_question SET
    enonce = "L'intégrale de f(x) = 2x est x² + C.",
    explication = "En effet, la primitive de 2x est x² + C."
WHERE enonce LIKE '%int%grale%' OR enonce LIKE '%grale%';

-- 6. Corriger les choix de réponse mal encodés
UPDATE quiz_choix SET texte = "f'(x) = 2x + 3" WHERE texte LIKE "%2x%3%" AND texte LIKE "%'%";
UPDATE quiz_choix SET texte = "f'(x) = x + 3"  WHERE texte LIKE "%x%3%" AND texte LIKE "%'%" AND texte NOT LIKE "%2x%";
UPDATE quiz_choix SET texte = "f'(x) = 2x"     WHERE texte LIKE "%2x%" AND texte NOT LIKE "%3%";
UPDATE quiz_choix SET texte = "f'(x) = 3x + 2" WHERE texte LIKE "%3x%2%" AND texte LIKE "%'%";

SELECT 'Encodage corrigé ✓' AS statut;
