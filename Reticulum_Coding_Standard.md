# Reticulum Coding Standard (Draft)

Version: 0.1

Obiettivo: Scrivere utility che sembrino parte integrante
dell'ecosistema Reticulum, seguendo le stesse convenzioni delle utility
ufficiali.

------------------------------------------------------------------------

## Filosofia

-   Usare esclusivamente API pubbliche di Reticulum.
-   Non reinventare protocolli già esistenti.
-   Lasciare che Reticulum gestisca rete, trasporto e affidabilità.
-   Lasciare che SQLite gestisca SQL.
-   Ogni modulo deve avere una sola responsabilità.
-   Preferire funzioni semplici a classi non necessarie.

------------------------------------------------------------------------

## Struttura tipica

main() ↓ parse_args() ↓ load/create identity ↓ inizializzazione
Reticulum ↓ esecuzione ↓ callback

------------------------------------------------------------------------

## Identity

Convenzioni osservate:

-   ogni utility possiede una propria Identity;
-   la Identity viene caricata da file;
-   se non esiste viene creata automaticamente;
-   è possibile specificarla tramite -i.

Da verificare nel dettaglio: - rncp - rnx - rnsh - rnid

------------------------------------------------------------------------

## Comunicazione

Preferire:

Request/Response API

quando rappresenta naturalmente il problema.

Usare Resource API quando devono essere trasferiti dati di grandi
dimensioni.

Non creare protocolli proprietari.

------------------------------------------------------------------------

## Link

Aprire il Link una volta.

Identificare il peer.

Lasciare la gestione della connessione a Reticulum.

------------------------------------------------------------------------

## Callback

Preferire callback piccole e leggibili.

Una callback = una responsabilità.

------------------------------------------------------------------------

## Logging

Usare RNS.log() per messaggi tecnici.

Usare print() solo per l'interazione con l'utente.

------------------------------------------------------------------------

## Configurazione

Seguire lo stile delle utility ufficiali.

Utilizzare argparse.

Opzioni corte e lunghe coerenti:

-i -v -q --config --version

------------------------------------------------------------------------

## Naming

Usare la terminologia Reticulum:

Identity Destination Link Request Response Resource Transport Announce

Evitare nomi presi dal mondo TCP se non necessari.

------------------------------------------------------------------------

## Principi per rSQLite

La CLI parla con l'utente.

transport.py parla con Reticulum.

rsqlite-server.py parla con SQLite.

Nessun modulo deve conoscere dettagli degli altri.

------------------------------------------------------------------------

## Prossima attività

Analizzare sistematicamente le utility ufficiali:

-   rncp
-   rnx
-   rnsh
-   rnprobe
-   rnpath
-   rnstatus
-   rnid
-   rnir

Per ogni utility annotare:

-   struttura
-   gestione Identity
-   configurazione
-   callback
-   logging
-   error handling
-   naming
-   API utilizzate

Ogni regola di questo documento dovrà essere collegata alla utility da
cui deriva.
