export DATIVETOP_IP = 127.0.0.1
export DATIVETOP_OLD_PORT = 5679
export DATIVETOP_OLD_SRC = src/old
export DATIVETOP_DATIVE_SRC = src/dative
export DATIVETOP_DATIVE_SERVERS_REL = dist/servers.json
export DATIVETOP_DATIVE_SERVERS = ${DATIVETOP_DATIVE_SRC}/${DATIVETOP_DATIVE_SERVERS_REL}

export OLD_DB_RDBMS = sqlite
export HERE = $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
export OLD_PERMANENT_STORE = oldinstances
export OLD_DB_DIRPATH = ${HERE}/${OLD_PERMANENT_STORE}/dbs
export OLD_SESSION_TYPE = file
export DFLT_DATIVETOP_OLD_NAME = myold

create-old-instance:  ## Create an OLD instance named OLD_NAME: create a directory structure for it, an SQLite database with tables pre-populated, and register it with Dative
	initialize_old ${DATIVETOP_OLD_SRC}/config.ini $(OLD_NAME); \
		python dativetop/scripts/register-old-with-dative.py create $(OLD_NAME)

destroy-old-instance:  ## Destroy OLD instance OLD_NAME's files on disk and its SQLite database and de-register it from Dative
	rm -r ${OLD_PERMANENT_STORE}/$(OLD_NAME) || true; \
	rm ${OLD_PERMANENT_STORE}/dbs/$(OLD_NAME).sqlite || true; \
		python dativetop/scripts/register-old-with-dative.py destroy $(OLD_NAME)

build-dative:  ## Build Dative: install NPM dependencies, compile/minify JS and reset its servers array
	cd ${DATIVETOP_DATIVE_SRC};\
		yarn;\
		grunt build;\
		echo "[]" > ${DATIVETOP_DATIVE_SERVERS_REL}

launch:  ## Launch DativeTop in development mode
	python -m dativetop

build-mac-os:  ## Build a DativeTop .app bundle for Mac OS
	initialize_old ${DATIVETOP_OLD_SRC}/config.ini ${DFLT_DATIVETOP_OLD_NAME}; \
		python dativetop/scripts/register-old-with-dative.py create ${DFLT_DATIVETOP_OLD_NAME}; \
		DFLT_DATIVETOP_OLD_NAME=${DFLT_DATIVETOP_OLD_NAME} beeware build macOS

run-mac-os:  ## Build and run DativeTop .app bundle for Mac OS
	beeware run macOS


help:  ## Print this help message.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

fart:
	export DFLT_DATIVETOP_OLD_NAME='myold'

.DEFAULT_GOAL := help
