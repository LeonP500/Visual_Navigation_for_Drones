# Literature Review: Visual Navigation for Low-Flying Drones

## Introduction

In GNSS-denied environments, Unmanned Aerial Vehicles (UAVs) must rely on alternative sensors to estimate their position and navigate safely. For low-flying drones (20-200 meters), visual navigation has become the dominant approach due to the lightweight nature of cameras and the rich contextual information they provide. 

This review focuses on recent research papers (2023-2024) that provide open-source implementations (**"Paper with Code"**), specifically addressing the problem of Map Matching and Terrain-Relative Navigation for UAVs.

## Key Research Papers and Open-Source Implementations

Recent advancements have shifted towards deep learning to address the "domain gap" between different flights, seasonal changes, or varying camera angles (e.g., comparing oblique drone views to top-down satellite imagery).

Here are the most notable recent "Paper with Code" implementations:

### 1. SDPL (Shifting-Dense Partition Learning)
*   **Year:** 2024 (ACM Multimedia Workshop on UAVs)
*   **Concept:** Focuses on the unique perspective distortions in UAV imagery compared to satellite maps. It shifts image partitions to find the best dense matches across different viewing angles.
*   **Paper with Code:** [Layumi/ACMMM2024Workshop-UAV](https://github.com/layumi/ACMMM2024Workshop-UAV)

### 2. SIVL (Season-Invariant GNSS-Denied Visual Localization)
*   **Year:** 2023 (IEEE Robotics and Automation Letters)
*   **Concept:** Specifically tackles the problem of localizing a UAV when the current environment looks different from the database map due to seasonal or lighting changes. It uses robust image similarity metrics.
*   **Paper with Code:** [aalto-intelligent-robotics/sivl](https://github.com/aalto-intelligent-robotics/sivl)

### 3. UAV Visual Localization System (Deep Feature Matching)
*   **Concept:** Implements state-of-the-art deep matching algorithms like LoFTR (Local Feature Matching with Transformers) and OmniGlue. It uses Python, PyTorch, and OpenCV to estimate positions by matching onboard camera images with pre-built maps.
*   **Open-Source Repo:** [erfgd/UAV-visual-localization-system](https://github.com/erfgd/UAV-visual-localization-system-image-matching-algorithms-based)

### 4. VisionUAV-Navigation (Classical Feature-Based)
*   **Concept:** For lightweight, real-time applications where domain gaps are smaller, classical methods still excel. This repository provides a robust pipeline combining multiple feature detectors (SIFT, ORB, BRISK) with outlier rejection techniques (like RANSAC) to match drone feeds against geo-referenced imagery.
*   **Open-Source Repo:** [sidharthmohannair/VisionUAV-Navigation](https://github.com/sidharthmohannair/VisionUAV-Navigation)

## Our Chosen Direction

For the specific assignment task—preprocessing a video with telemetry and localizing a new video stream against it—we are building a custom, lightweight pipeline inspired by the classical feature matching techniques found in **VisionUAV-Navigation**. 

Instead of a heavy PyTorch dependency (like LoFTR or SDPL), we implemented an **ORB-based BFMatcher** in OpenCV. This guarantees real-time performance while still following the architectural principles of modern cross-view localization papers.
