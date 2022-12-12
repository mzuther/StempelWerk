-- ========================================================================== --
-- demonstration of creating multiple files from a single template
-- ========================================================================== --

-- this file was auto-generated from the following template:
-- 10-templates/00-stencils/20-sql_create_stored_procedure.sql.jinja


CREATE OR ALTER PROCEDURE DEMO.MultiFile_Procedure
WITH EXECUTE AS CALLER
AS
BEGIN
    BEGIN TRY
        BEGIN TRANSACTION;

        -- prepare data for merge
        WITH Load_Data AS
        (
            SELECT
                Key_Column_1,
                Key_Column_2,
                -- -------------------------------------------------- --
                String_Column,
                -- -------------------------------------------------- --
                -- this comment has been added automatically
                Integer_Column
            FROM
                DEMO.MultiFile_Source
        ),
        Converted_Value AS
        (
            SELECT
                Load_Data.*,
                -- -------------------------------------------------- --
                Numeric_Column =
                    CAST(2 AS DECIMAL(10, 5)) *
                    CAST(3.14159 AS DECIMAL(10, 5)) *
                    CAST(Integer_Column AS DECIMAL(10, 5))
            FROM
                Load_Data
        )
        -- merge data from tgt into src
        MERGE
            DEMO.MultiFile_Target AS tgt
        USING
            Converted_Value AS src
        ON
            tgt.Key_Column_1 = src.Key_Column_1 AND
            tgt.Key_Column_2 = src.Key_Column_2
        -- update rows that exist and differ between source and target table
        -- (https://stackoverflow.com/a/8948461)
        WHEN MATCHED AND EXISTS
            (
                SELECT
                    tgt.String_Column,
                    -- -------------------------------------------------- --
                    -- this comment has been added automatically
                    tgt.Integer_Column,
                    tgt.Numeric_Column

                EXCEPT

                SELECT
                    src.String_Column,
                    -- -------------------------------------------------- --
                    -- this comment has been added automatically
                    src.Integer_Column,
                    src.Numeric_Column
            )
            THEN UPDATE SET
                tgt.String_Column                  = src.String_Column,
                -- -------------------------------------------------- --
                tgt.Integer_Column                 = src.Integer_Column,
                tgt.Numeric_Column                 = src.Numeric_Column
        -- insert rows that are not in target table
        WHEN NOT MATCHED BY TARGET
            THEN INSERT
            (
                Key_Column_1,
                Key_Column_2,
                -- -------------------------------------------------- --
                String_Column,
                -- -------------------------------------------------- --
                Integer_Column,
                Numeric_Column
            )
            VALUES
            (
                src.Key_Column_1,
                src.Key_Column_2,
                -- -------------------------------------------------- --
                src.String_Column,
                -- -------------------------------------------------- --
                src.Integer_Column,
                src.Numeric_Column
            )
        -- delete rows that are not in source table
        WHEN NOT MATCHED BY SOURCE
            THEN DELETE;

        COMMIT TRANSACTION;
    END TRY

    BEGIN CATCH
        ROLLBACK TRANSACTION;

        -- propagate exception to caller
        THROW;
    END CATCH
END;
GO

ALTER AUTHORIZATION ON OBJECT::DEMO.MultiFile_Procedure TO SCHEMA OWNER;
GO
