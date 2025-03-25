# Rapport de Santé de la Base de Données

**Date :** 2025-03-25 14:29:48.767131

## Connexions Actives
**Nombre total :** 1

## Requêtes Longues

## Verrous
- Table : pg_authid_oid_index, Mode : AccessShareLock, Nombre : 1
- Table : pg_authid_rolname_index, Mode : AccessShareLock, Nombre : 1
- Table : pg_stat_activity, Mode : AccessShareLock, Nombre : 1
- Table : pg_database_oid_index, Mode : AccessShareLock, Nombre : 1
- Table : pg_locks, Mode : AccessShareLock, Nombre : 1
- Table : pg_authid, Mode : AccessShareLock, Nombre : 1
- Table : pg_database_datname_index, Mode : AccessShareLock, Nombre : 1
- Table : pg_database, Mode : AccessShareLock, Nombre : 1

## Statistiques de Performance des Tables
- Table : orders
  - Scans séquentiels : 58
  - Scans par index : 9681
  - Tuples vivants : 99441
  - Tuples morts : 0
- Table : order_reviews
  - Scans séquentiels : 34
  - Scans par index : 7046
  - Tuples vivants : 98410
  - Tuples morts : 0
- Table : product_categories
  - Scans séquentiels : 32
  - Scans par index : 76
  - Tuples vivants : 0
  - Tuples morts : 0
- Table : products
  - Scans séquentiels : 31
  - Scans par index : 123
  - Tuples vivants : 32951
  - Tuples morts : 0
- Table : order_items
  - Scans séquentiels : 48
  - Scans par index : 2517
  - Tuples vivants : 112650
  - Tuples morts : 0
- Table : customers
  - Scans séquentiels : 66
  - Scans par index : 9456
  - Tuples vivants : 99441
  - Tuples morts : 0
- Table : data_dictionary
  - Scans séquentiels : 2
  - Scans par index : None
  - Tuples vivants : 0
  - Tuples morts : 0
- Table : sellers
  - Scans séquentiels : 28
  - Scans par index : 74
  - Tuples vivants : 3095
  - Tuples morts : 0
- Table : geolocation
  - Scans séquentiels : 0
  - Scans par index : 0
  - Tuples vivants : 0
  - Tuples morts : 0
- Table : order_payments
  - Scans séquentiels : 0
  - Scans par index : 0
  - Tuples vivants : 0
  - Tuples morts : 0
