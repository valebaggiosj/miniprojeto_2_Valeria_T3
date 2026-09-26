-- Lista 15 empregados
SELECT * FROM HR.EMPLOYEES FETCH FIRST 15 ROWS ONLY

-- Lista 15 empregos
SELECT * FROM HR.JOBS FETCH FIRST 15 ROWS ONLY

-- Lista 15 departamentos
SELECT * FROM HR.DEPARTMENTS FETCH FIRST 15 ROWS ONLY

-- Lista histórico de trabalho
SELECT * FROM HR.JOB_HISTORY FETCH FIRST 15 ROWS ONLY


--  Salários por departamento e cargo 
SELECT
    TRIM(E.FIRST_NAME) || ' ' || TRIM(E.LAST_NAME)  AS NOME_COMPLETO,
    J.JOB_TITLE                                     AS CARGO,
    D.DEPARTMENT_NAME                               AS DEPARTAMENTO,
    E.HIRE_DATE                                     AS DATA_CONTRATACAO,
    H.START_DATE                                    AS DATA_INICIO_TRABALHO,
    H.END_DATE                                      AS DATA_FIM_TRABALHO,
    E.SALARY                                        AS SALARIO_CONTRATADO,
    J.MIN_SALARY                                    AS SALARIO_MIN,
    J.MAX_SALARY                                    AS SALARIO_MAX
FROM HR.EMPLOYEES        E
LEFT JOIN HR.JOBS        J ON E.JOB_ID = J.JOB_ID
LEFT JOIN HR.DEPARTMENTS D ON E.DEPARTMENT_ID = D.DEPARTMENT_ID
LEFT JOIN HR.JOB_HISTORY H ON E.EMPLOYEE_ID = H.EMPLOYEE_ID

