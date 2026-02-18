from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, ProcessData, BatchRecord, get_db
from pydantic import BaseModel
import pandas as pd
import io
from datetime import datetime
import logging
from typing import List, Optional
import json

logger = logging.getLogger(__name__)
router = APIRouter()

# Schemas
class ProcessDataInput(BaseModel):
    batch_id: str
    unit: str
    temperature_c: Optional[float] = None
    pressure_bar: Optional[float] = None
    flow_rate: Optional[float] = None
    rpm: Optional[float] = None
    power_kw: Optional[float] = None
    level_percent: Optional[float] = None
    parameters: Optional[dict] = None

class BatchRecordInput(BaseModel):
    batch_id: str
    product_name: str
    yield_percent: float
    purity_percent: float
    cost_per_kg: float
    energy_kwh: float
    solvent_kg: float
    duration_hours: float
    status: str = "Completed"

# Manual data entry
@router.post("/manual-entry/batch")
async def add_batch_record(data: BatchRecordInput, db: Session = Depends(get_db)):
    """Add manual batch record"""
    try:
        db_batch = BatchRecord(
            batch_id=data.batch_id,
            product_name=data.product_name,
            yield_percent=data.yield_percent,
            purity_percent=data.purity_percent,
            cost_per_kg=data.cost_per_kg,
            energy_kwh=data.energy_kwh,
            solvent_kg=data.solvent_kg,
            duration_hours=data.duration_hours,
            status=data.status,
            end_time=datetime.utcnow()
        )
        db.add(db_batch)
        db.commit()
        db.refresh(db_batch)
        return {"success": True, "batch_id": data.batch_id}
    except Exception as e:
        logger.error(f"Error adding batch record: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/manual-entry/process-data")
async def add_process_data(data: ProcessDataInput, db: Session = Depends(get_db)):
    """Add manual process data point"""
    try:
        db_data = ProcessData(
            batch_id=data.batch_id,
            unit=data.unit,
            timestamp=datetime.utcnow(),
            temperature_c=data.temperature_c,
            pressure_bar=data.pressure_bar,
            flow_rate=data.flow_rate,
            rpm=data.rpm,
            power_kw=data.power_kw,
            level_percent=data.level_percent,
            parameters=data.parameters or {}
        )
        db.add(db_data)
        db.commit()
        return {"success": True, "message": "Data added"}
    except Exception as e:
        logger.error(f"Error adding process data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Excel upload
@router.post("/upload/excel")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload Excel file with batch and process data"""
    try:
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="File must be .xlsx, .xls, or .csv")
        
        contents = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # Auto-detect sheet type
        if 'batch_id' in df.columns and 'yield_percent' in df.columns:
            # Batch records
            records_added = 0
            for _, row in df.iterrows():
                db_batch = BatchRecord(
                    batch_id=str(row.get('batch_id')),   
                    product_name=str(row.get('product_name', 'Unknown')),
                    yield_percent=float(row.get('yield_percent', 0)),
                    purity_percent=float(row.get('purity_percent', 0)),
                    cost_per_kg=float(row.get('cost_per_kg', 0)),
                    energy_kwh=float(row.get('energy_kwh', 0)),
                    solvent_kg=float(row.get('solvent_kg', 0)),
                    duration_hours=float(row.get('duration_hours', 0)),
                    status=str(row.get('status', 'Completed'))
                )
                db.add(db_batch)
                records_added += 1
            db.commit()
            return {
                "success": True, 
                "records_added": records_added,
                "type": "batch_records"
            }
        
        elif 'unit' in df.columns and 'temperature_c' in df.columns:
            # Process data
            records_added = 0
            for _, row in df.iterrows():
                db_data = ProcessData(
                    batch_id=str(row.get('batch_id')),
                    unit=str(row.get('unit')),
                    timestamp=pd.to_datetime(row.get('timestamp', datetime.utcnow())),
                    temperature_c=float(row.get('temperature_c')) if pd.notna(row.get('temperature_c')) else None,
                    pressure_bar=float(row.get('pressure_bar')) if pd.notna(row.get('pressure_bar')) else None,
                    flow_rate=float(row.get('flow_rate')) if pd.notna(row.get('flow_rate')) else None,
                    rpm=float(row.get('rpm')) if pd.notna(row.get('rpm')) else None,
                    power_kw=float(row.get('power_kw')) if pd.notna(row.get('power_kw')) else None,
                    level_percent=float(row.get('level_percent')) if pd.notna(row.get('level_percent')) else None,
                    parameters={}
                )
                db.add(db_data)
                records_added += 1
            db.commit()
            return {
                "success": True, 
                "records_added": records_added,
                "type": "process_data"
            }
        else:
            raise HTTPException(status_code=400, detail="Excel format not recognized")
    
    except Exception as e:
        logger.error(f"Error uploading Excel: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Get uploaded data
@router.get("/batches")
async def get_batches(db: Session = Depends(get_db)):
    """Get all batch records"""
    batches = db.query(BatchRecord).all()
    return {
        "total": len(batches),
        "batches": [
            {
                "batch_id": b.batch_id,
                "product_name": b.product_name,
                "yield_percent": b.yield_percent,
                "cost_per_kg": b.cost_per_kg,
                "energy_kwh": b.energy_kwh,
                "status": b.status
            } for b in batches
        ]
    }

@router.get("/process-data/{batch_id}")
async def get_process_data(batch_id: str, db: Session = Depends(get_db)):
    """Get process data for a specific batch"""
    data = db.query(ProcessData).filter(ProcessData.batch_id == batch_id).all()
    return {
        "batch_id": batch_id,
        "records": len(data),
        "data": [
            {
                "unit": d.unit,
                "timestamp": d.timestamp.isoformat(),
                "temperature_c": d.temperature_c,
                "pressure_bar": d.pressure_bar,
                "flow_rate": d.flow_rate,
                "power_kw": d.power_kw
            } for d in data
        ]
    }