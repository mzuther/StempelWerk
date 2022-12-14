-- ========================================================================== --
-- demonstration of creating multiple files from a single template
-- ========================================================================== --

-- this file was auto-generated from the following template:
-- 10-templates/00-stencils/10-sql_create_table.sql.jinja


DROP TABLE IF EXISTS DEMO.SingleFile_Table;

CREATE TABLE DEMO.SingleFile_Table
(
    Key_Column_1     NVARCHAR(200) COLLATE Latin1_General_100_CI_AS NOT NULL,
    Key_Column_2     NVARCHAR(200) COLLATE Latin1_General_100_CI_AS NOT NULL,
    -- -------------------------------------------------- --
    -- this comment has been added automatically
    Integer_Column   INT DEFAULT 10,
    Numeric_Column   DECIMAL(10, 5) NOT NULL,

    -- add primary key
    CONSTRAINT PK_SingleFile_Table
    PRIMARY KEY CLUSTERED
    (
        Key_Column_1,
        Key_Column_2
    )
);

ALTER AUTHORIZATION ON OBJECT::DEMO.SingleFile_Table TO SCHEMA OWNER;
GO
