/* ============================================================
   001_init_schema.sql
   Initial schema for the Inventory Expiry Tracker.
   Target: Microsoft SQL Server (T-SQL)
   ============================================================ */

-- Create the database if it does not already exist
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'InventoryExpiryDB')
BEGIN
    CREATE DATABASE InventoryExpiryDB;
END
GO

USE InventoryExpiryDB;
GO

/* ------------------------------------------------------------
   Products
   One row per distinct product that can be stocked.
   ------------------------------------------------------------ */
IF OBJECT_ID(N'dbo.Products', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Products
    (
        ProductID   INT            IDENTITY(1, 1) NOT NULL,
        Barcode     NVARCHAR(64)   NOT NULL,
        Name        NVARCHAR(200)  NOT NULL,
        Category    NVARCHAR(100)  NULL,
        CONSTRAINT PK_Products PRIMARY KEY (ProductID),
        CONSTRAINT UQ_Products_Barcode UNIQUE (Barcode)
    );
END
GO

/* ------------------------------------------------------------
   Deliveries
   A batch of a product received into inventory, with a
   use-by date used to drive expiry alerts.
   ------------------------------------------------------------ */
IF OBJECT_ID(N'dbo.Deliveries', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Deliveries
    (
        DeliveryID  INT       IDENTITY(1, 1) NOT NULL,
        ProductID   INT       NOT NULL,
        Quantity    INT       NOT NULL,
        UseByDate   DATE      NOT NULL,
        ReceivedAt  DATETIME  NOT NULL CONSTRAINT DF_Deliveries_ReceivedAt DEFAULT (GETDATE()),
        CONSTRAINT PK_Deliveries PRIMARY KEY (DeliveryID),
        CONSTRAINT FK_Deliveries_Products FOREIGN KEY (ProductID)
            REFERENCES dbo.Products (ProductID)
    );
END
GO

/* ------------------------------------------------------------
   Alerts
   An expiry alert raised against a delivery.
   ------------------------------------------------------------ */
IF OBJECT_ID(N'dbo.Alerts', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Alerts
    (
        AlertID           INT       IDENTITY(1, 1) NOT NULL,
        DeliveryID        INT       NOT NULL,
        AlertGeneratedAt  DATETIME  NOT NULL CONSTRAINT DF_Alerts_AlertGeneratedAt DEFAULT (GETDATE()),
        Status            NVARCHAR(50) NOT NULL,
        CONSTRAINT PK_Alerts PRIMARY KEY (AlertID),
        CONSTRAINT FK_Alerts_Deliveries FOREIGN KEY (DeliveryID)
            REFERENCES dbo.Deliveries (DeliveryID)
    );
END
GO
