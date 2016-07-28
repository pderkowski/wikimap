#include "zoom.hpp"
#include <vector>
#include <algorithm>
#include <cassert>

Zoom::Zoom(const std::vector<Point>& points, int pointsPerTile)
: tree_(helpers::getBounds(points), pointsPerTile)
{
    for (auto it = points.begin(); it != points.end(); ++it) {
        tree_.insert(*it);
    }
}

std::vector<Point> Zoom::getPoints(const Bounds& bounds, int zoomLevel) const {
    assert(tree_.getBounds().contain(bounds));

    auto closedBounds = helpers::getClosedBounds(bounds);

    auto topLeft = closedBounds.getTopLeftCorner();
    auto bottomRight = closedBounds.getBottomRightCorner();

    auto tlCoords = tree_.getBucketCoords(topLeft, zoomLevel);
    auto brCoords = tree_.getBucketCoords(bottomRight, zoomLevel);

    std::vector<Bucket> buckets;

    for (int x = tlCoords.x(); x <= brCoords.x(); ++x) {
        for (int y = tlCoords.y(); y <= brCoords.y(); ++y) {
            auto bucket = tree_.getBucket(BucketCoords(x, y, zoomLevel));
            if (std::find(buckets.begin(), buckets.end(), bucket) == buckets.end()) {
                buckets.push_back(bucket);
            }
        }
    }

    std::vector<Point> points;
    for (const auto& bucket : buckets) {
        auto bucketPoints = bucket.getPoints();
        points.insert(points.end(), bucketPoints.begin(), bucketPoints.end());
    }

    return points;
}