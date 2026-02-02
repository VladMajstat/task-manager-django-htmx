# SQL Answers

1) Get all statuses, not repeating, alphabetically ordered

```sql
SELECT DISTINCT status
FROM tasks
ORDER BY status;
```

2) Get the count of all tasks in each project, order by tasks count descending

```sql
SELECT p.id, p.name, COUNT(t.id) AS task_count
FROM projects AS p
LEFT JOIN tasks AS t ON t.project_id = p.id
GROUP BY p.id, p.name
ORDER BY task_count DESC;
```

3) Get the count of all tasks in each project, order by projects names

```sql
SELECT p.id, p.name, COUNT(t.id) AS task_count
FROM projects AS p
LEFT JOIN tasks AS t ON t.project_id = p.id
GROUP BY p.id, p.name
ORDER BY p.name;
```

4) Get the tasks for all projects having the name beginning with "N" letter

```sql
SELECT t.*
FROM tasks AS t
JOIN projects AS p ON p.id = t.project_id
WHERE p.name LIKE 'N%'
ORDER BY p.name, t.id;
```

5) Get the list of all projects containing the 'a' letter in the middle of the name, and show the tasks count near each project.
   Note: projects can exist without tasks, and tasks can have project_id = NULL, so we must use LEFT JOIN.

```sql
SELECT p.id, p.name, COUNT(t.id) AS task_count
FROM projects AS p
LEFT JOIN tasks AS t ON t.project_id = p.id
WHERE p.name ILIKE '%a%'
  AND p.name NOT ILIKE 'a%'
  AND p.name NOT ILIKE '%a'
GROUP BY p.id, p.name
ORDER BY p.name;
```

6) Get the list of tasks with duplicate names. Order alphabetically

```sql
SELECT name
FROM tasks
GROUP BY name
HAVING COUNT(*) > 1
ORDER BY name;
```

7) Get the list of tasks having several exact matches of both name and status, from the project 'Delivery'. Order by matches count

```sql
SELECT t.name, t.status, COUNT(*) AS matches
FROM tasks AS t
JOIN projects AS p ON p.id = t.project_id
WHERE p.name = 'Delivery'
GROUP BY t.name, t.status
HAVING COUNT(*) > 1
ORDER BY matches DESC, t.name, t.status;
```

8) Get the list of project names having more than 10 tasks in status 'completed'. Order by project_id

```sql
SELECT p.id, p.name
FROM projects AS p
JOIN tasks AS t ON t.project_id = p.id
WHERE t.status = 'completed'
GROUP BY p.id, p.name
HAVING COUNT(*) > 10
ORDER BY p.id;
```
