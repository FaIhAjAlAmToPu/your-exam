from fastapi import APIRouter, Depends, HTTPException


router = APIRouter(
    prefix="/exam",
    tags=["exam"],
    responses={404: {"description": "Not found"}},
)


@router.get("/results")
async def read_item():
    return {"results": "idk"}


@router.put(
    "/{item_id}",
    tags=["custom"],
    responses={403: {"description": "Operation forbidden"}},
)
async def update_item(item_id: str):
    if item_id != "plumbus":
        raise HTTPException(
            status_code=403, detail="You can only update the item: plumbus"
        )
    return {"item_id": item_id, "name": "The great Plumbus"}