from core.data_source.rtsp_source import RTSPSource
from core.data_source.disk_source import DiskSource
from core.segmentation.yolo_segmenter import YOLOSegmenter
from core.segmentation.gsam_segmenter import GSAMSegmenter
from core.metrics_calculator import MetricsCalculator
from core.network.udp_sender import UDPSender
from core.postprocessor import Postprocessor


def build_models(config):
    if config['mode'] == "debug":
        data_source = DiskSource()
    else:
        data_source = RTSPSource(url=config['source'])
        
    if config['model'] == "yolo":
        segmenter = YOLOSegmenter(config['weights']['yolo_weights'])
    else:
        segmenter = GSAMSegmenter()
        
    metrics_calculator = MetricsCalculator()
    network_sender = UDPSender(
        ip=config['network']['udp_ip'],
        port=config['network']['udp_port']
    )
    postprocessor = Postprocessor()

    return data_source, segmenter, metrics_calculator, postprocessor, network_sender