# This code is proprietary to AquaTrak. Unauthorized use is strictly prohibited.

"""
Tests for InSAR Land Subsidence Monitoring Module
"""

import pytest
import numpy as np
from datetime import datetime
from unittest.mock import Mock, patch

from src.modules.insar_subsidence.models import (
    SubsidenceData, SubsidenceResult, SubsidencePoint, 
    SubsidenceLevel, SatelliteType
)
from src.modules.insar_subsidence.processor import InSARSubsidenceProcessor

class TestSubsidenceData:
    """Test SubsidenceData model"""
    
    def test_valid_subsidence_data(self):
        """Test creating valid subsidence data"""
        data = SubsidenceData(
            satellite_type=SatelliteType.SENTINEL_1,
            image1_path="test_image1.tif",
            image2_path="test_image2.tif",
            date1=datetime(2023, 1, 1),
            date2=datetime(2023, 1, 15),
            bounds={
                'min_lat': 35.0,
                'max_lat': 36.0,
                'min_lon': 51.0,
                'max_lon': 52.0
            }
        )
        
        assert data.satellite_type == SatelliteType.SENTINEL_1
        assert data.image1_path == "test_image1.tif"
        assert data.image2_path == "test_image2.tif"
        assert data.bounds['min_lat'] == 35.0
    
    def test_invalid_dates(self):
        """Test validation of dates"""
        with pytest.raises(ValueError, match="date2 must be after date1"):
            SubsidenceData(
                satellite_type=SatelliteType.SENTINEL_1,
                image1_path="test_image1.tif",
                image2_path="test_image2.tif",
                date1=datetime(2023, 1, 15),
                date2=datetime(2023, 1, 1),
                bounds={
                    'min_lat': 35.0,
                    'max_lat': 36.0,
                    'min_lon': 51.0,
                    'max_lon': 52.0
                }
            )
    
    def test_invalid_bounds(self):
        """Test validation of geographic bounds"""
        with pytest.raises(ValueError, match="min_lat must be less than max_lat"):
            SubsidenceData(
                satellite_type=SatelliteType.SENTINEL_1,
                image1_path="test_image1.tif",
                image2_path="test_image2.tif",
                date1=datetime(2023, 1, 1),
                date2=datetime(2023, 1, 15),
                bounds={
                    'min_lat': 36.0,
                    'max_lat': 35.0,
                    'min_lon': 51.0,
                    'max_lon': 52.0
                }
            )

class TestSubsidencePoint:
    """Test SubsidencePoint model"""
    
    def test_valid_subsidence_point(self):
        """Test creating valid subsidence point"""
        point = SubsidencePoint(
            lat=35.6892,
            lon=51.3890,
            deformation_rate=15.5,
            coherence=0.8,
            uncertainty=0.1,
            level=SubsidenceLevel.MEDIUM
        )
        
        assert point.lat == 35.6892
        assert point.lon == 51.3890
        assert point.deformation_rate == 15.5
        assert point.coherence == 0.8
        assert point.level == SubsidenceLevel.MEDIUM
    
    def test_invalid_coherence(self):
        """Test coherence validation"""
        with pytest.raises(ValueError):
            SubsidencePoint(
                lat=35.6892,
                lon=51.3890,
                deformation_rate=15.5,
                coherence=1.5,  # Invalid: > 1.0
                uncertainty=0.1,
                level=SubsidenceLevel.MEDIUM
            )

class TestInSARSubsidenceProcessor:
    """Test InSAR Subsidence Processor"""
    
    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return InSARSubsidenceProcessor()
    
    @pytest.fixture
    def sample_data(self):
        """Create sample input data"""
        return SubsidenceData(
            satellite_type=SatelliteType.SENTINEL_1,
            image1_path="test_image1.tif",
            image2_path="test_image2.tif",
            date1=datetime(2023, 1, 1),
            date2=datetime(2023, 1, 15),
            bounds={
                'min_lat': 35.0,
                'max_lat': 36.0,
                'min_lon': 51.0,
                'max_lon': 52.0
            }
        )
    
    def test_processor_initialization(self, processor):
        """Test processor initialization"""
        assert processor.coherence_threshold == 0.3
        assert processor.deformation_threshold == 0.01
        assert processor.min_points == 100
    
    def test_risk_level_determination(self, processor):
        """Test risk level determination"""
        assert processor._determine_risk_level(3.0) == SubsidenceLevel.LOW
        assert processor._determine_risk_level(10.0) == SubsidenceLevel.MEDIUM
        assert processor._determine_risk_level(25.0) == SubsidenceLevel.HIGH
        assert processor._determine_risk_level(35.0) == SubsidenceLevel.CRITICAL
    
    def test_area_calculation(self, processor):
        """Test area calculation"""
        bounds = {
            'min_lat': 35.0,
            'max_lat': 36.0,
            'min_lon': 51.0,
            'max_lon': 52.0
        }
        area = processor._calculate_area(bounds)
        assert area > 0
        assert isinstance(area, float)
    
    @patch('src.modules.insar_subsidence.processor.InSARSubsidenceProcessor._load_satellite_image')
    @patch('src.modules.insar_subsidence.processor.InSARSubsidenceProcessor._perform_insar_processing')
    @patch('src.modules.insar_subsidence.processor.InSARSubsidenceProcessor._apply_bounds')
    @patch('src.modules.insar_subsidence.processor.InSARSubsidenceProcessor._generate_measurement_points')
    @patch('src.modules.insar_subsidence.processor.InSARSubsidenceProcessor._calculate_statistics')
    @patch('src.modules.insar_subsidence.processor.InSARSubsidenceProcessor._assess_risk_levels')
    @patch('src.modules.insar_subsidence.processor.InSARSubsidenceProcessor._identify_critical_areas')
    @patch('src.modules.insar_subsidence.processor.InSARSubsidenceProcessor._generate_output_files')
    def test_process_method(
        self, 
        mock_generate_output_files,
        mock_identify_critical_areas,
        mock_assess_risk_levels,
        mock_calculate_statistics,
        mock_generate_points,
        mock_apply_bounds,
        mock_perform_processing,
        mock_load_image,
        processor,
        sample_data
    ):
        """Test the main process method"""
        # Mock return values
        mock_load_image.return_value = (np.random.rand(100, 100), {'crs': 'EPSG:4326'})
        mock_perform_processing.return_value = (np.random.rand(100, 100), np.random.rand(100, 100))
        mock_apply_bounds.return_value = (np.random.rand(100, 100), np.random.rand(100, 100))
        mock_generate_points.return_value = []
        mock_calculate_statistics.return_value = {'mean': 0.0, 'std': 1.0}
        mock_assess_risk_levels.return_value = {SubsidenceLevel.LOW: 0}
        mock_identify_critical_areas.return_value = []
        mock_generate_output_files.return_value = {'test': 'test.tif'}
        
        # Test processing
        result = processor.process(sample_data)
        
        assert isinstance(result, SubsidenceResult)
        assert result.satellite_type == SatelliteType.SENTINEL_1
        assert result.analysis_id is not None
        assert result.processing_time > 0
    
    def test_validate_input_missing_files(self, processor, sample_data):
        """Test input validation with missing files"""
        with patch('os.path.exists', return_value=False):
            with pytest.raises(Exception):
                processor._validate_input(sample_data)
    
    def test_generate_alert(self, processor):
        """Test alert generation"""
        # Create mock result
        result = Mock()
        result.points = [
            SubsidencePoint(
                lat=35.6892,
                lon=51.3890,
                deformation_rate=35.0,
                coherence=0.8,
                uncertainty=0.1,
                level=SubsidenceLevel.CRITICAL
            )
        ]
        
        alerts = processor.generate_alert(result)
        
        assert len(alerts) == 1
        assert alerts[0].risk_level == SubsidenceLevel.CRITICAL
        assert alerts[0].severity == "high"
    
    def test_generate_report(self, processor):
        """Test report generation"""
        # Create mock result
        result = Mock()
        result.analysis_id = "test-id"
        result.area_covered = 100.0
        result.points = []
        result.statistics = {'mean': 0.0, 'std': 1.0}
        result.risk_summary = {SubsidenceLevel.LOW: 0}
        result.output_files = {}
        
        report = processor.generate_report(result)
        
        assert report.analysis_result == result
        assert report.executive_summary is not None
        assert len(report.key_findings) > 0
        assert len(report.recommendations) > 0

class TestIntegration:
    """Integration tests"""
    
    def test_end_to_end_processing(self):
        """Test end-to-end processing workflow"""
        # This would test the complete workflow with real data
        # For now, just verify the structure
        processor = InSARSubsidenceProcessor()
        assert processor is not None
        assert hasattr(processor, 'process')
        assert hasattr(processor, 'generate_alert')
        assert hasattr(processor, 'generate_report') 