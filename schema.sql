-- Tabella Utenti
CREATE TABLE Utenti (
    ID_Utente INT AUTO_INCREMENT PRIMARY KEY,
    Email VARCHAR(255) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL, -- Considerare l'hashing della password
    Nome VARCHAR(100),
    Cognome VARCHAR(100),
    Ruolo ENUM('Admin', 'Volontario') DEFAULT 'Volontario',
    DataCreazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella Famiglie
CREATE TABLE Famiglie (
    ID_Famiglia INT AUTO_INCREMENT PRIMARY KEY,
    NomeFamiglia VARCHAR(255) NOT NULL,
    ReferenteNome VARCHAR(100),
    ReferenteCognome VARCHAR(100),
    NumeroMembri INT,
    NumeroUomini INT DEFAULT 0,
    NumeroDonne INT DEFAULT 0,
    NumeroBambini INT DEFAULT 0,
    Indirizzo VARCHAR(255),
    NumeroTelefono VARCHAR(20),
    Email VARCHAR(255),
    SettimanaDistribuzione INT, -- Es. 1, 2, 3, 4 per le settimane del mese
    TipoDistribuzione ENUM('Casa', 'Centro'),
    Note TEXT,
    DataRegistrazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella Prodotti (per l'inventario)
CREATE TABLE Prodotti (
    ID_Prodotto INT AUTO_INCREMENT PRIMARY KEY,
    NomeProdotto VARCHAR(255) NOT NULL,
    Descrizione TEXT,
    UnitaMisura VARCHAR(50) -- Es. kg, litri, pezzi
);

-- Tabella Inventario
CREATE TABLE Inventario (
    ID_VoceInventario INT AUTO_INCREMENT PRIMARY KEY,
    ID_Prodotto INT,
    Quantita DECIMAL(10, 2) NOT NULL,
    DataScadenza DATE,
    DataInserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    DataUltimaModifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (ID_Prodotto) REFERENCES Prodotti(ID_Prodotto)
);

-- Tabella CarichiInventario (per tracciare le entrate di prodotti)
CREATE TABLE CarichiInventario (
    ID_Carico INT AUTO_INCREMENT PRIMARY KEY,
    ID_Prodotto INT,
    QuantitaCaricata DECIMAL(10, 2) NOT NULL,
    DataCarico DATE NOT NULL,
    Fornitore VARCHAR(255),
    Note TEXT,
    DataRegistrazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ID_UtenteRegistrazione INT,
    FOREIGN KEY (ID_Prodotto) REFERENCES Prodotti(ID_Prodotto),
    FOREIGN KEY (ID_UtenteRegistrazione) REFERENCES Utenti(ID_Utente)
);

-- Tabella Progetti
CREATE TABLE Progetti (
    ID_Progetto INT AUTO_INCREMENT PRIMARY KEY,
    NomeProgetto VARCHAR(255) NOT NULL,
    Descrizione TEXT,
    DataInizio DATE,
    DataFine DATE,
    Stato ENUM('In Corso', 'Completato', 'Pianificato') DEFAULT 'Pianificato',
    ImmagineURL VARCHAR(255)
);

-- Tabella Attivita (legate ai progetti o generali)
CREATE TABLE Attivita (
    ID_Attivita INT AUTO_INCREMENT PRIMARY KEY,
    ID_Progetto INT NULL, -- Può essere NULL se l'attività non è legata a un progetto specifico
    NomeAttivita VARCHAR(255) NOT NULL,
    Descrizione TEXT,
    DataAttivita DATETIME,
    Luogo VARCHAR(255),
    ImmagineURL VARCHAR(255),
    FOREIGN KEY (ID_Progetto) REFERENCES Progetti(ID_Progetto)
);

-- Tabella Notizie
CREATE TABLE Notizie (
    ID_Notizia INT AUTO_INCREMENT PRIMARY KEY,
    Titolo VARCHAR(255) NOT NULL,
    Contenuto TEXT NOT NULL,
    DataPubblicazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Autore VARCHAR(100), -- Potrebbe essere un ID_Utente se l'autore è un utente del sistema
    ImmagineURL VARCHAR(255),
    Categoria VARCHAR(100) -- Es. Eventi, Progetti, Aggiornamenti
);

-- Tabella Distribuzioni
CREATE TABLE Distribuzioni (
    ID_Distribuzione INT AUTO_INCREMENT PRIMARY KEY,
    ID_Famiglia INT,
    DataDistribuzione DATE NOT NULL,
    Note TEXT,
    ID_VolontarioConsegna INT,
    Stato ENUM('Pianificata', 'Completata', 'Annullata') DEFAULT 'Pianificata',
    DataCreazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ID_Famiglia) REFERENCES Famiglie(ID_Famiglia),
    FOREIGN KEY (ID_VolontarioConsegna) REFERENCES Utenti(ID_Utente)
);

-- Tabella DettaglioDistribuzione (prodotti specifici distribuiti in una distribuzione)
CREATE TABLE DettaglioDistribuzione (
    ID_DettaglioDistribuzione INT AUTO_INCREMENT PRIMARY KEY,
    ID_Distribuzione INT,
    ID_Prodotto INT,
    QuantitaDistribuita DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (ID_Distribuzione) REFERENCES Distribuzioni(ID_Distribuzione),
    FOREIGN KEY (ID_Prodotto) REFERENCES Prodotti(ID_Prodotto)
);

-- Tabella Appuntamenti (per le distribuzioni o altre attività)
CREATE TABLE Appuntamenti (
    ID_Appuntamento INT AUTO_INCREMENT PRIMARY KEY,
    ID_Famiglia INT NULL, -- Può essere legato a una famiglia
    ID_Attivita INT NULL, -- O a un'attività specifica
    Titolo VARCHAR(255),
    DataOraAppuntamento DATETIME NOT NULL,
    Luogo VARCHAR(255),
    Note TEXT,
    Stato ENUM('Pianificato', 'Confermato', 'Annullato', 'Completato') DEFAULT 'Pianificato',
    DataCreazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ID_Famiglia) REFERENCES Famiglie(ID_Famiglia),
    FOREIGN KEY (ID_Attivita) REFERENCES Attivita(ID_Attivita)
);

-- Indici per migliorare le performance delle query
CREATE INDEX idx_famiglie_nome ON Famiglie(NomeFamiglia);
CREATE INDEX idx_prodotti_nome ON Prodotti(NomeProdotto);
CREATE INDEX idx_inventario_prodotto ON Inventario(ID_Prodotto);
CREATE INDEX idx_inventario_scadenza ON Inventario(DataScadenza);
CREATE INDEX idx_distribuzioni_famiglia ON Distribuzioni(ID_Famiglia);
CREATE INDEX idx_distribuzioni_data ON Distribuzioni(DataDistribuzione);
CREATE INDEX idx_notizie_data ON Notizie(DataPubblicazione);
CREATE INDEX idx_progetti_nome ON Progetti(NomeProgetto);
CREATE INDEX idx_attivita_data ON Attivita(DataAttivita);
CREATE INDEX idx_appuntamenti_data ON Appuntamenti(DataOraAppuntamento);

-- Aggiunta di alcuni dati iniziali (opzionale, per testing)
-- Utente Admin di esempio
INSERT INTO Utenti (Email, Password, Nome, Cognome, Ruolo) VALUES ('admin@example.com', '$2b$12$abcdefghijklmnopqrstuv.abcdefghijklmnopqrstuv.abcdefghijkl', 'Admin', 'User', 'Admin');
-- Volontario di esempio
INSERT INTO Utenti (Email, Password, Nome, Cognome, Ruolo) VALUES ('volontario@example.com', '$2b$12$abcdefghijklmnopqrstuv.abcdefghijklmnopqrstuv.abcdefghijkl', 'Mario', 'Rossi', 'Volontario');
-- Nota: Le password sono placeholder bcrypt-like. Devono essere generate correttamente dall'applicazione.

-- Prodotto di esempio
INSERT INTO Prodotti (NomeProdotto, Descrizione, UnitaMisura) VALUES ('Pasta di semola', 'Pasta di grano duro, formato spaghetti', 'kg');
INSERT INTO Prodotti (NomeProdotto, Descrizione, UnitaMisura) VALUES ('Riso Arborio', 'Riso per risotti', 'kg');
INSERT INTO Prodotti (NomeProdotto, Descrizione, UnitaMisura) VALUES ('Olio Extra Vergine di Oliva', 'Olio di oliva spremuto a freddo', 'litri');
INSERT INTO Prodotti (NomeProdotto, Descrizione, UnitaMisura) VALUES ('Latte UHT Parzialmente Scremato', 'Latte a lunga conservazione', 'litri');

-- Voce inventario di esempio
INSERT INTO Inventario (ID_Prodotto, Quantita, DataScadenza) VALUES (1, 50.00, '2024-12-31');
INSERT INTO Inventario (ID_Prodotto, Quantita, DataScadenza) VALUES (2, 30.00, '2024-11-15');

-- Famiglia di esempio
INSERT INTO Famiglie (NomeFamiglia, ReferenteNome, ReferenteCognome, NumeroMembri, NumeroUomini, NumeroDonne, NumeroBambini, Indirizzo, NumeroTelefono, Email, SettimanaDistribuzione, TipoDistribuzione)
VALUES ('Famiglia Rossi', 'Giovanni', 'Rossi', 4, 2, 1, 1, 'Via Roma 1', '3331234567', 'fam.rossi@email.com', 1, 'Casa');

-- Notizia di esempio
INSERT INTO Notizie (Titolo, Contenuto, Autore, Categoria) VALUES
('Nuova Iniziativa di Raccolta Fondi', 'Partecipa alla nostra nuova iniziativa per sostenere le famiglie bisognose.', 'Admin User', 'Eventi');

-- Progetto di esempio
INSERT INTO Progetti (NomeProgetto, Descrizione, DataInizio, Stato) VALUES
('Supporto Alimentare Continuativo', 'Progetto per garantire un aiuto alimentare costante alle famiglie in difficoltà.', '2023-01-01', 'In Corso');

-- Attività di esempio
INSERT INTO Attivita (ID_Progetto, NomeAttivita, Descrizione, DataAttivita, Luogo) VALUES
(1, 'Distribuzione Pacchi Alimentari Mensile', 'Distribuzione mensile di pacchi alimentari.', '2024-07-15 10:00:00', 'Sede Associazione');

-- Distribuzione di esempio
INSERT INTO Distribuzioni (ID_Famiglia, DataDistribuzione, ID_VolontarioConsegna, Stato) VALUES
(1, '2024-07-01', 2, 'Completata');

-- Dettaglio Distribuzione di esempio
INSERT INTO DettaglioDistribuzione (ID_Distribuzione, ID_Prodotto, QuantitaDistribuita) VALUES
(1, 1, 2.00); -- 2kg di Pasta
INSERT INTO DettaglioDistribuzione (ID_Distribuzione, ID_Prodotto, QuantitaDistribuita) VALUES
(1, 4, 6.00); -- 6 litri di Latte
