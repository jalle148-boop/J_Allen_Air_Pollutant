General summary:

The pickle file contains a dictionary with a hierarchical structure:

**Top Level (dict):**
- Single key: descriptive string identifying the dataset
  - Format: `{State}_{County}_{Site}_{frequency}_{parameter_code}_{duration}_{year}_{aggregation_method}`
  - Example: `'North Carolina_Beaufort_6_daily_42401_7d_2004_daily_zscore'`

**Value: List of Shapelets**
- Contains 50 shapelet objects (in this example)
- Each shapelet is a dictionary with 15 keys

**Shapelet Dictionary Keys (visible from example):**
- `shapelet`: numpy ndarray containing the shapelet values (length matches `length_days`)
- `length_days`: int (7 days in this example)
- `quality`: float64 metric
- `start_date`: datetime.date object
- `end_date`: datetime.date object
- 10 additional keys (truncated in the report)

**Structure Summary:**
```
{
  "<dataset_identifier>": [
    {shapelet_dict_1},
    {shapelet_dict_2},
    ...
    {shapelet_dict_50}
  ]
}
```

Example:

Max depth: 6
Max items per container: 5

Structure:
- dict (keys=1)
  - key: 'North Carolina_Beaufort_6_daily_42401_7d_2004_daily_zscore'
    - list (len=50)
      - index: 0
        - dict (keys=15)
          - key: 'shapelet'
            - ndarray: array([-0.23496516, -0.33816179, -0.45167778, -0.93670169, -0.98436862,
        1.00339323,  1.9424818 ])
          - key: 'length_days'
            - int: 7
          - key: 'quality'
            - float64: np.float64(0.996539553861555)
          - key: 'start_date'
            - date: datetime.date(2004, 1, 1)
          - key: 'end_date'
            - date: datetime.date(2004, 1, 7)
          - <truncated keys at 5 items>
      - index: 1
        - dict (keys=15)
          - key: 'shapelet'
            - ndarray: array([-0.3220964 , -0.43514802, -0.91818783, -0.96565978,  1.0139707 ,
        1.94921772, -0.3220964 ])
          - key: 'length_days'
            - <cycle detected>
          - key: 'quality'
            - float64: np.float64(1.0047429830993775)
          - key: 'start_date'
            - date: datetime.date(2004, 1, 2)
          - key: 'end_date'
            - date: datetime.date(2004, 1, 8)
          - <truncated keys at 5 items>
      - index: 2
        - dict (keys=15)
          - key: 'shapelet'
            - ndarray: array([-0.37646372, -0.84851264, -0.89490443,  1.03968236,  1.95364915,
       -0.26598442, -0.6074663 ])
          - key: 'length_days'
            - <cycle detected>
          - key: 'quality'
            - float64: np.float64(1.0520752699290437)
          - key: 'start_date'
            - date: datetime.date(2004, 1, 3)
          - key: 'end_date'
            - date: datetime.date(2004, 1, 9)
          - <truncated keys at 5 items>
      - index: 3
        - dict (keys=15)
          - key: 'shapelet'
            - ndarray: array([-0.94425831, -0.99112949,  0.96344851,  1.88685986, -0.35571049,
       -0.7007211 ,  0.14151102])
          - key: 'length_days'
            - <cycle detected>
          - key: 'quality'
            - float64: np.float64(1.0306642929816976)
          - key: 'start_date'
            - date: datetime.date(2004, 1, 4)
          - key: 'end_date'
            - date: datetime.date(2004, 1, 10)
          - <truncated keys at 5 items>
      - index: 4
        - dict (keys=15)
          - key: 'shapelet'
            - ndarray: array([-1.19264972,  0.91296669,  1.90773388, -0.50812924, -0.87980025,
        0.02751466, -0.26763602])
          - key: 'length_days'
            - <cycle detected>
          - key: 'quality'
            - float64: np.float64(0.8881058582682435)
          - key: 'start_date'
            - date: datetime.date(2004, 1, 5)
          - key: 'end_date'
            - date: datetime.date(2004, 1, 11)
          - <truncated keys at 5 items>
      - <truncated items at 5 items>