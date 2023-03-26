HOME_DIR = /home/kingdo
OPENWHISK_PROJECT_HOME ?= $(HOME_DIR)/IdeaProjects/openwhisk
WSK_CLI ?= $(OPENWHISK_PROJECT_HOME)/bin/wsk
WSK_CONFIG_FILE=$(HOME_DIR)/.wskprops

DOCKER_IMAGE = kingdo/action-python-v3.10
DOCKER_IMAGE_TAG = latest


resize/.resize_action_is_deployed: resize/data resize/__main__.py
	cd resize && zip -r resize_action data __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update ML-Prediction-resize resize/resize_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch resize/.resize_action_is_deployed
.PHONY: resize_action_invoke
resize_action_invoke: resize/.resize_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result ML-Prediction-resize --param name World


predict/.predict_action_is_deployed: predict/__main__.py
	cd predict && zip -r predict_action data __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update ML-Prediction-predict predict/predict_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch predict/.predict_action_is_deployed
.PHONY: predict_action_invoke
predict_action_invoke: predict/.predict_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result ML-Prediction-predict --param name World


render/.render_action_is_deployed: render/__main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update ML-Prediction-render render/__main__.py \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch render/.render_action_is_deployed
.PHONY: render_action_invoke
render_action_invoke: render/.render_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result ML-Prediction-render --param-file render/param.json


.sequence_action_is_deployed: resize/.resize_action_is_deployed predict/.predict_action_is_deployed render/.render_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update ML-Prediction-sequence --sequence ML-Prediction-resize,ML-Prediction-predict,ML-Prediction-render
	touch .sequence_action_is_deployed

sequence_action_invoke: .sequence_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result ML-Prediction-sequence

clean:
	rm .sequence_action_is_deployed resize/.resize_action_is_deployed predict/.predict_action_is_deployed render/.render_action_is_deployed
	rm -rf predict/predict_action.zip resize/resize_action.zip
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete ML-Prediction-sequence
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete --result ML-Prediction-render
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete --result ML-Prediction-predict
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete --result ML-Prediction-resize