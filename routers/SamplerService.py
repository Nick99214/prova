import logging
from fastapi import APIRouter, HTTPException
from exceptions.ExceptionHandler import ExceptionHandler
from service.Service import Service
from utility import Constants
from model.ResponseModel import Response
from model.RequestModel import Request
from config import config


settings = config.Settings()

router = APIRouter(
    prefix="/bki/api/v1",
    tags=["sampler"]
)


@router.post("/get_sample")
async def extract_sample(request : Request):
    """
    Endpoint to extract a sample based on the provided request.

    Parameters:
    - request (Request): The request object containing sampling parameters.

    Returns:
    Response: The response object containing the result of the sampling process.
    """

    if request.sample_size <= 0:
        raise HTTPException(status_code=400, detail="The 'sample_size' field must be a positive integer.")

    if request.type not in [Constants.ODG_TYPE, Constants.INTERVENTI_TYPE]:
        raise HTTPException(status_code=400, detail="The 'type' field must be '{}' or '{}'.".format(Constants.ODG_TYPE, Constants.INTERVENTI_TYPE))

    if request.start_sampling_date >= request.end_sampling_date:
        raise HTTPException(status_code=400, detail="The start sampling date must be before the end date.")

    if not(request.annotator_1 and request.annotator_2):
        raise HTTPException(status_code=400, detail="Both annotators must be specified.")


    try:
        service = Service(request)
        logging.info("Starting sampling pipeline")
        sample_id = service.do_sampling_pipeline()
        if sample_id:
            return Response(result=Constants.OK, response_message = Constants.OK_RESPONSE_MESSAGE,sample_id = sample_id)
        else:
            return Response(result=Constants.KO, response_message = Constants.KO_RESPONSE_MESSAGE_NOT_ENOUGH_DATA, sample_id=sample_id)
    except Exception as e:
        exception = ExceptionHandler(e)
        logging.error("Unexpected error: {}".format(exception.stacktrace))
        raise HTTPException(status_code=500, detail=exception.message)
