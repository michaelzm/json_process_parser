import re
# this function takes as input a list of subprocesses: start:condition:sequence:end and trasnforms them into a connected list of elements
def parse_json_response_into_elements(parsed_json):
  id_counter = 1
  shared_id = {}
  unique_id = {}
  elements = []

  for subprocess in parsed_json["sub_process_list"]:
    start_element = subprocess["start"]
    if start_element not in shared_id.values():
      shared_id[f"id_{id_counter}"] = start_element
      id_counter += 1

    end_element = subprocess["end"]
    if end_element not in shared_id.values():
      shared_id[f"id_{id_counter}"] = end_element
      id_counter += 1

    #everything in between start and end is treated as unique item
    start_key = next((k for k, v in shared_id.items() if v == start_element), None)
    end_key = next((k for k, v in shared_id.items() if v == end_element), None)
    start_end_key = f"{start_key}_{end_key}"
    unique_id[start_end_key] = {}
    
    condition = subprocess["condition"]
    tasks = subprocess["sequence_of_tasks"]
    
    for task in tasks:
      unique_id[start_end_key][f"id_{id_counter}"] = task
      id_counter += 1

    all_tasks = [start_element] + tasks + [end_element]

    for i in range(1, len(all_tasks)):
      print("length of elements", len(all_tasks))
      print("current at i", i)
      path_start = False
      path_end = False
      if i-1 == 0:
        path_start = True
      if i == len(all_tasks) -1:
        path_end = True
      
      print(path_start, path_end)

      from_elem = all_tasks[i-1]
      to_elem = all_tasks[i]
      outgoing_labels = []
      if path_start:
        # we fetch from shared keys
        start_key = next((k for k, v in shared_id.items() if v == from_elem), None)
        outgoing_labels = [condition]
      else:
        #we fetch from unique keys
        start_key = next((k for k, v in unique_id[start_end_key].items() if v == from_elem), None)

      if path_end:
        #we fetch from shared keys
        end_key = next((k for k, v in shared_id.items() if v == to_elem), None)

      else:
        #we fetch from unique keys
        end_key = next((k for k, v in unique_id[start_end_key].items() if v == to_elem), None)

      element = {"id": start_key, "type":"", "label":from_elem, "outgoing":[end_key], "outgoing_labels":outgoing_labels}
      elements.append(element)
  print("all elements so far ",elements)
  #add end elements without simultanous being start element as new end element
  # this must be done as in per above code, only from with outgoing = to are added, so no end elements
  print("so far all shared ids as ", shared_id)
  for subprocess in parsed_json["sub_process_list"]:
    print("\n")
    print(subprocess)
    end_element = subprocess["end"]
    path_end_key = next((k for k, v in shared_id.items() if v == end_element), None)
    print("key that belongs to end element ", end_element, " identified as ", path_end_key)
    #check if end element is tracked as process element after run above
    all_ids = [e["id"] for e in elements]
    print(" so far all ids of single elements ", all_ids)
    if path_end_key not in all_ids:
      element = {"id": path_end_key, "type":"", "label":end_element, "outgoing":[], "outgoing_labels":[]}
      print("found path end and adding element ", element)
      elements.append(element)
    else:
       print("for this, already tracked element")
  return elements

def densen_connected_elements(elements):
    combined = {}

    for item in elements:
        key = item['id']
        if key in combined:
            # Combine the 'outgoing' and 'outgoing_labels' lists if id already exists
            combined[key]['outgoing'].extend(item['outgoing'])
            combined[key]['outgoing_labels'].extend(item['outgoing_labels'])
        else:
            combined[key] = item.copy()
    result_list = list(combined.values())
    return result_list

def identify_type(dense_elements):
    for e in dense_elements:
        outgoing_elements = len(e["outgoing"])
        if e["id"] == "1":
            e["type"] = "startEvent"
        elif outgoing_elements == 0:
            e["type"] = "endEvent"
        elif outgoing_elements == 1:
            e["type"] = "userTask"
        else:
            e["type"] = "exclusiveGateway"
        
        if e["type"] != "exclusiveGateway" and "outgoing_labels" in e:
           del e["outgoing_labels"]

        regex_label = re.sub(r'[^\w\s]', '', e["label"]) if isinstance(e["label"], str) else e["label"]
        e["label"] = regex_label

    return dense_elements

elements = parse_json_response_into_elements(json_parsed)
dense_elements = densen_connected_elements(elements)
dense_elements = identify_type(dense_elements)