HOME_DIR = /home/kingdo
OPENWHISK_PROJECT_HOME ?= $(HOME_DIR)/IdeaProjects/openwhisk
WSK_CLI ?= $(OPENWHISK_PROJECT_HOME)/bin/wsk
WSK_CONFIG_FILE=$(HOME_DIR)/.wskprops

DOCKER_IMAGE = kingdo/action-python-v3.10
DOCKER_IMAGE_TAG = latest

flowcontrol/.flowcontrol_action_is_deployed: flowcontrol/__main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update FINRA-Faastorage-flowcontrol flowcontrol/__main__.py \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch flowcontrol/.flowcontrol_action_is_deployed
.PHONY: flowcontrol_action_invoke
flowcontrol_action_invoke: flowcontrol/.flowcontrol_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result FINRA-Faastorage-flowcontrol --param-file flowcontrol/param.json

marginBalance/.marginBalance_action_is_deployed: marginBalance/__main__.py
	cd marginBalance && zip -r marginBalance_action data __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update FINRA-Faastorage-marginBalance marginBalance/marginBalance_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch marginBalance/.marginBalance_action_is_deployed
.PHONY: marginBalance_action_invoke
marginBalance_action_invoke: marginBalance/.marginBalance_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result FINRA-Faastorage-marginBalance --param-file marginBalance/param.json

lastpx/.lastpx_action_is_deployed: lastpx/__main__.py
	cd lastpx && zip -r lastpx_action data __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update FINRA-Faastorage-lastpx lastpx/lastpx_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch lastpx/.lastpx_action_is_deployed
.PHONY: lastpx_action_invoke
lastpx_action_invoke: lastpx/.lastpx_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result FINRA-Faastorage-lastpx --param-file flowcontrol/param.json

volume/.volume_action_is_deployed: volume/__main__.py
	cd volume && zip -r volume_action data __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update FINRA-Faastorage-volume volume/volume_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch volume/.volume_action_is_deployed
.PHONY: volume_action_invoke
volume_action_invoke: volume/.volume_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result FINRA-Faastorage-volume --param-file flowcontrol/param.json

trddate/.trddate_action_is_deployed: trddate/__main__.py
	cd trddate && zip -r trddate_action data __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update FINRA-Faastorage-trddate trddate/trddate_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch trddate/.trddate_action_is_deployed
.PHONY: trddate_action_invoke
trddate_action_invoke: trddate/.trddate_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result FINRA-Faastorage-trddate --param-file flowcontrol/param.json

side/.side_action_is_deployed: side/__main__.py
	cd side && zip -r side_action data __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update FINRA-Faastorage-side side/side_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch side/.side_action_is_deployed
.PHONY: side_action_invoke
side_action_invoke: side/.side_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result FINRA-Faastorage-side --param-file flowcontrol/param.json

marketdata/.marketdata_action_is_deployed: marketdata/__main__.py
	cd marketdata && zip -r marketdata_action data __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update FINRA-Faastorage-marketdata marketdata/marketdata_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch marketdata/.marketdata_action_is_deployed
.PHONY: marketdata_action_invoke
marketdata_action_invoke: marketdata/.marketdata_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result FINRA-Faastorage-marketdata --param-file flowcontrol/param.json


.action_is_deployed: flowcontrol/__main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update FINRA-Faastorage-flow flowcontrol/__main__.py \
  --docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .action_is_deployed

action_invoke: .action_is_deployed lastpx/.lastpx_action_is_deployed side/.side_action_is_deployed marketdata/.marketdata_action_is_deployed trddate/.trddate_action_is_deployed volume/.volume_action_is_deployed marginBalance/.marginBalance_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result FINRA-Faastorage-flow --param-file flowcontrol/param.json

clean:
	rm -rf .action_is_deployed .action_is_deployed lastpx/.lastpx_action_is_deployed side/.side_action_is_deployed marketdata/.marketdata_action_is_deployed trddate/.trddate_action_is_deployed volume/.volume_action_is_deployed marginBalance/.marginBalance_action_is_deployed
	rm -rf marketdata/marketdata_action.zip lastpx/lastpx_action.zip side/side_action.zip trddate/trddate_action.zip volume/volume_action.zip marginBalance/marginBalance_action.zip
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete FINRA-Faastorage-flow
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete FINRA-Faastorage-marketdata
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete FINRA-Faastorage-trddate
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete FINRA-Faastorage-volume
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete FINRA-Faastorage-side
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete FINRA-Faastorage-lastpx
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete FINRA-Faastorage-marginBalance
