-- Lista 15 localizações
SELECT * FROM HR.LOCATIONS FETCH FIRST 15 ROWS ONLY

-- Lista 15 paises
SELECT * FROM HR.COUNTRIES FETCH FIRST 15 ROWS ONLY

-- Lista regioes
SELECT * FROM HR.REGIONS 



-- Confirmando que todos os departamentos estão a sua localização identificada 
SELECT * FROM HR.DEPARTMENTS WHERE LOCATION_ID IS NULL

-- Um dos empregados não está relacionado a um departamento. 
-- Vou usar o filtro na consulta, pois se solicitam infromações de localização 
--   e, sem esse campo preenchido, não tem dados complementares para esse empregado.
SELECT * FROM HR.EMPLOYEES WHERE DEPARTMENT_ID IS NULL



-- Funcionários por região, incluindo informações de localização
SELECT
    TRIM(E.FIRST_NAME) || ' ' || TRIM(E.LAST_NAME)  AS NOME_COMPLETO,
    D.DEPARTMENT_NAME                               AS DEPARTAMENTO,
    L.STREET_ADDRESS                                AS ENDERECO,
    L.POSTAL_CODE                                   AS CODIGO_POSTAL,
    L.CITY                                          AS CIDADE,
    L.STATE_PROVINCE                                AS ESTADO,
    C.COUNTRY_NAME                                  AS PAIS,
    R.REGION_NAME                                   AS REGIAO
FROM HR.EMPLOYEES        E 
LEFT JOIN HR.DEPARTMENTS D ON E.DEPARTMENT_ID = D.DEPARTMENT_ID
LEFT JOIN HR.LOCATIONS   L ON D.LOCATION_ID = L.LOCATION_ID
LEFT JOIN HR.COUNTRIES   C ON L.COUNTRY_ID = C.COUNTRY_ID
LEFT JOIN HR.REGIONS     R ON C.REGION_ID = R.REGION_ID
WHERE E.DEPARTMENT_ID IS NOT NULL