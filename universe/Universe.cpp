#include "Universe.h"

#include "../util/AppInterface.h"
#include "Building.h"
#include "Effect.h"
#include "Fleet.h"
#include "../util/DataTable.h"
#include "../util/MultiplayerCommon.h"
#include "../util/OptionsDB.h"
#include "../util/Directories.h"
#include "Planet.h"
#include "Predicates.h"
#include "../util/Random.h"
#include "Special.h"
#include "../Empire/Empire.h"
#include "../Empire/EmpireManager.h"
#include "Ship.h"
#include "ShipDesign.h"
#include "System.h"
#include "UniverseObject.h"

#ifdef FREEORION_BUILD_HUMAN
#include "../client/human/HumanClientApp.h"
#endif

#ifdef FREEORION_BUILD_SERVER
#include "../server/ServerApp.h"
#endif

#include <SDL/SDL_byteorder.h>

#include <boost/filesystem/fstream.hpp>
#include <boost/graph/dijkstra_shortest_paths.hpp>
#include <boost/graph/breadth_first_search.hpp>

#include <cmath>
#include <stdexcept>

namespace {
    const double  OFFROAD_SLOWDOWN_FACTOR = 1000000000.0; // the factor by which non-starlane travel is slower than starlane travel

    DataTableMap& UniverseDataTables()
    {
        static DataTableMap map;
        if (map.empty()) {
            std::string settings_dir = GetOptionsDB().Get<std::string>("settings-dir");
            if (!settings_dir.empty() && settings_dir[settings_dir.size() - 1] != '/')
                settings_dir += '/';

            LoadDataTables(settings_dir + "universe_tables.txt", map);
        }
        return map;
    }

    // used to short-circuit the use of BFS (breadth-first search) or Dijkstra's algorithm for pathfinding when it finds the desired destination system
    struct PathFindingShortCircuitingVisitor : public boost::base_visitor<PathFindingShortCircuitingVisitor>
    {
        typedef boost::on_finish_vertex event_filter;

        struct FoundDestination {}; // exception type thrown when destination is found

        PathFindingShortCircuitingVisitor(int dest_system) : destination_system(dest_system) {}
        template <class Vertex, class Graph>
        void operator()(Vertex u, Graph& g)
        {
            if (static_cast<int>(u) == destination_system)
                throw FoundDestination();
        }
        const int destination_system;
    };

    void LoadSystemNames(std::list<std::string>& names)
    {
        boost::filesystem::ifstream ifs(GetSettingsDir() / "starnames.txt");
        while (ifs) {
            std::string latest_name;
            std::getline(ifs, latest_name);
            if (latest_name != "") {
                names.push_back(latest_name.substr(0, latest_name.find_last_not_of(" \t") + 1)); // strip off trailing whitespace
            }
        }
    }

    ////////////////////////////////////////////////////////////////
    // templated implementations of Universe graph search methods //
    ////////////////////////////////////////////////////////////////

    // returns the \a graph index for system with \a system_id
    template <class Graph>
    int SystemGraphIndex(const Graph& graph, int system_id)
    {
        typedef typename boost::property_map<Graph, Universe::vertex_system_pointer_t>::const_type ConstSystemPointerPropertyMap;
        ConstSystemPointerPropertyMap pointer_property_map = boost::get(Universe::vertex_system_pointer_t(), graph);

        for (unsigned int i = 0; i < boost::num_vertices(graph); ++i) {
            const int loop_sys_id = pointer_property_map[i]->ID();    // get system ID of this vertex
            if (loop_sys_id == system_id)
                return i;
        }

        throw std::out_of_range("SystemGraphIndex cannot be found due to invalid system ID");
        return -1;
    }

    /* returns the path between vertices \a system1_id and \a system2_id of \a graph that travels the shorest 
       distance on starlanes, and the path length.  If system1_id is the same vertex as system2_id, the path 
       has just that system in it, and the path lenth is 0.  If there is no path between the two vertices, then
       the list is empty and the path length is -1.0 */
    template <class Graph>
    std::pair<std::list<System*>, double> ShortestPathImpl(const Graph& graph, int system1_id, int system2_id, double linear_distance)
    {
        typedef typename boost::property_map<Graph, Universe::vertex_system_pointer_t>::const_type ConstSystemPointerPropertyMap;
        typedef typename boost::property_map<Graph, boost::vertex_index_t>::const_type             ConstIndexPropertyMap;
        typedef typename boost::property_map<Graph, boost::edge_weight_t>::const_type              ConstEdgeWeightPropertyMap;

        std::pair<std::list<System*>, double> retval;

        ConstIndexPropertyMap index_map = boost::get(boost::vertex_index, graph);
        ConstEdgeWeightPropertyMap edge_weight_map = boost::get(boost::edge_weight, graph);

        int system1_index = SystemGraphIndex(graph, system1_id);
        int system2_index = SystemGraphIndex(graph, system2_id);

        ConstSystemPointerPropertyMap pointer_property_map = boost::get(Universe::vertex_system_pointer_t(), graph);

        // early exit if systems are the same
        if (system1_id == system2_id) {
            System* system = pointer_property_map[system2_index];
            retval.first.push_back(system);
            retval.second = 0.0;    // no jumps needed -> 0 distance
            return retval;
        }

        /* initializing all vertices' predecessors to themselves prevents endless loops when back traversing the tree in the case where
           one of the end systems is system 0, because systems that are not connected to the root system (system2) are not visited
           by the search, and so their predecessors are left unchanged.  Default initialization of the vector may be 0 or undefined
           which could lead to out of bounds errors, or endless loops if a system's default predecessor is 0 (debug mode), and 0's
           predecessor is that system */
        std::vector<int> predecessors(boost::num_vertices(graph));
        std::vector<double> distances(boost::num_vertices(graph));
        for (unsigned int i = 0; i < boost::num_vertices(graph); ++i) {
            predecessors[i] = i;
            distances[i] = -1.0;
        }


        // do the actual path finding using verbose boost magic...
        try {
            boost::dijkstra_shortest_paths(graph, system1_index, &predecessors[0], &distances[0], edge_weight_map, index_map, 
                                           std::less<double>(), std::plus<double>(), std::numeric_limits<int>::max(), 0, 
                                           boost::make_dijkstra_visitor(PathFindingShortCircuitingVisitor(system2_index)));
        } catch (const PathFindingShortCircuitingVisitor::FoundDestination& fd) {
            // catching this just means that the destination was found, and so the algorithm was exited early, via exception
        }


        int current_system = system2_index;
        while (predecessors[current_system] != current_system) {
            retval.first.push_front(pointer_property_map[current_system]);
            current_system = predecessors[current_system];
        }
        retval.second = distances[system2_index];

        if (retval.first.empty()) {
            // there is no path between the specified nodes
            retval.second = -1.0;
            return retval;
        } else {
            // add start system to path, as it wasn't added by traversing predecessors array
            retval.first.push_front(pointer_property_map[system1_index]);
        }

        return retval;
    }

    /* returns the path between vertices \a system1_id and \a system2_id of \a graph that takes the fewest 
       number of jumps (edge traversals), and the number of jumps this path takes.  If system1_id is the same
       vertex as system2_id, the path has just that system in it, and the path lenth is 0.  If there is no
       path between the two vertices, then the list is empty and the path length is -1 */
    template <class Graph>
    std::pair<std::list<System*>, int> LeastJumpsPathImpl(const Graph& graph, int system1_id, int system2_id)
    {
        typedef typename boost::property_map<Graph, Universe::vertex_system_pointer_t>::const_type ConstSystemPointerPropertyMap;

        ConstSystemPointerPropertyMap pointer_property_map = boost::get(Universe::vertex_system_pointer_t(), graph);
        std::pair<std::list<System*>, int> retval;

        int system1_index = SystemGraphIndex(graph, system1_id);
        int system2_index = SystemGraphIndex(graph, system2_id);

        // early exit if systems are the same
        if (system1_id == system2_id) {
            System* system = pointer_property_map[system2_index];
            retval.first.push_back(system);
            retval.second = 0;  // no jumps needed
            return retval;
        }

        /* initializing all vertices' predecessors to themselves prevents endless loops when back traversing the tree in the case where
           one of the end systems is system 0, because systems that are not connected to the root system (system2) are not visited
           by the search, and so their predecessors are left unchanged.  Default initialization of the vector may be 0 or undefined
           which could lead to out of bounds errors, or endless loops if a system's default predecessor is 0, (debug mode) and 0's
           predecessor is that system */
        std::vector<int> predecessors(boost::num_vertices(graph));
        for (unsigned int i = 0; i < boost::num_vertices(graph); ++i)
            predecessors[i] = i;
        
        
        // do the actual path finding using verbose boost magic...
        try {
            boost::queue<int> buf;
            std::vector<int> colors(boost::num_vertices(graph));
            boost::breadth_first_search(graph, system1_index, buf,
                                        boost::make_bfs_visitor(std::make_pair(PathFindingShortCircuitingVisitor(system2_index),
                                                                               boost::record_predecessors(&predecessors[0],
                                                                                                          boost::on_tree_edge()))),
                                        &colors[0]);
        } catch (const PathFindingShortCircuitingVisitor::FoundDestination& fd) {
            // catching this just means that the destination was found, and so the algorithm was exited early, via exception
        }


        int current_system = system2_index;
        while (predecessors[current_system] != current_system) {
            retval.first.push_front(pointer_property_map[current_system]);
            current_system = predecessors[current_system];
        }
        retval.second = retval.first.size() - 1;    // number of jumps is number of systems in path minus one for the starting system

        if (retval.first.empty()) {
            // there is no path between the specified nodes
            retval.second = -1;
        } else {
            // add start system to path, as it wasn't added by traversing predecessors array
            retval.first.push_front(pointer_property_map[system1_index]);
        }
        
        return retval;
    }

    template <class Graph>
    bool SystemReachableImpl(const Graph& graph, int system_id)
    {
        return boost::in_degree(SystemGraphIndex(graph, system_id), graph);
    }

    template <class Graph>
    std::map<double, System*> ImmediateNeighborsImpl(const Graph& graph, int system_id)
    {
        typedef typename Graph::out_edge_iterator OutEdgeIterator;
        typedef typename boost::property_map<Graph, Universe::vertex_system_pointer_t>::const_type ConstSystemPointerPropertyMap;
        typedef typename boost::property_map<Graph, boost::edge_weight_t>::const_type ConstEdgeWeightPropertyMap;

        std::map<double, System*> retval;
        ConstEdgeWeightPropertyMap edge_weight_map = boost::get(boost::edge_weight, graph);
        ConstSystemPointerPropertyMap pointer_property_map = boost::get(Universe::vertex_system_pointer_t(), graph);
        std::pair<OutEdgeIterator, OutEdgeIterator> edges = boost::out_edges(SystemGraphIndex(graph, system_id), graph);
        for (OutEdgeIterator it = edges.first; it != edges.second; ++it) {
            retval[edge_weight_map[*it]] = pointer_property_map[boost::target(*it, graph)];
        }
        return retval;
    }
}

/////////////////////////////////////////////
// struct Universe::EdgeVisibilityFilter
/////////////////////////////////////////////
Universe::EdgeVisibilityFilter::EdgeVisibilityFilter() :
    m_graph(0),
    m_empire(0)
{}

Universe::EdgeVisibilityFilter::EdgeVisibilityFilter(const SystemGraph* graph, int empire_id) :
    m_graph(graph),
    m_empire(Empires().Lookup(empire_id))
{}

bool Universe::EdgeVisibilityFilter::CanSeeAtLeastOneSystem(const Empire* empire, int system1, int system2)
{
    return empire->HasExploredSystem(system1) || empire->HasExploredSystem(system2);
}


/////////////////////////////////////////////
// struct Universe::EffectAccountingInfo
/////////////////////////////////////////////
Universe::EffectAccountingInfo::EffectAccountingInfo() :
    source_id(UniverseObject::INVALID_OBJECT_ID),
    caused_by_empire_id(-1),
    cause_type(INVALID_EFFECTS_GROUP_CAUSE_TYPE),
    specific_cause(""),
    meter_change(0.0),
    running_meter_total(Meter::METER_MIN)
{}


/////////////////////////////////////////////
// class Universe
/////////////////////////////////////////////
// static(s)
const bool Universe::ALL_OBJECTS_VISIBLE = false;
double Universe::s_universe_width = 1000.0;
bool Universe::s_inhibit_universe_object_signals = false;
int Universe::s_encoding_empire = ALL_EMPIRES;

Universe::Universe()
{}

const Universe& Universe::operator=(Universe& rhs)
{
    for (ObjectMap::iterator it = m_objects.begin(); it != m_objects.end(); ++it) {
        delete it->second;
    }
    m_objects.clear();
    for (ObjectMap::iterator it = m_destroyed_objects.begin(); it != m_destroyed_objects.end(); ++it) {
        delete it->second;
    }
    m_objects.clear();
    m_destroyed_objects.clear();
    m_last_allocated_object_id = rhs.m_last_allocated_object_id;
    m_last_allocated_design_id = rhs.m_last_allocated_design_id;
    m_objects = rhs.m_objects;
    rhs.m_objects.clear();
    m_destroyed_objects = rhs.m_destroyed_objects;
    rhs.m_destroyed_objects.clear();
    InitializeSystemGraph();
    return *this;
}

Universe::~Universe()
{
    for (ObjectMap::iterator it = m_objects.begin(); it != m_objects.end(); ++it)
        delete it->second;
    for (ObjectMap::iterator it = m_destroyed_objects.begin(); it != m_destroyed_objects.end(); ++it)
        delete it->second;
}

const UniverseObject* Universe::Object(int id) const
{
    const_iterator it = m_objects.find(id);
    return (it != m_objects.end() ? it->second : 0);
}

UniverseObject* Universe::Object(int id)
{
    iterator it = m_objects.find(id);
    return (it != m_objects.end() ? it->second : 0);
}

Universe::ConstObjectVec Universe::FindObjects(const UniverseObjectVisitor& visitor) const
{
    ConstObjectVec retval;
    for (ObjectMap::const_iterator it = m_objects.begin(); it != m_objects.end(); ++it) {
        if (UniverseObject* obj = it->second->Accept(visitor))
            retval.push_back(obj);
    }
    return retval;
}

Universe::ObjectVec Universe::FindObjects(const UniverseObjectVisitor& visitor)
{
    ObjectVec retval;
    for (ObjectMap::iterator it = m_objects.begin(); it != m_objects.end(); ++it) {
        if (UniverseObject* obj = it->second->Accept(visitor))
            retval.push_back(obj);
    }
    return retval;
}

Universe::ObjectIDVec Universe::FindObjectIDs(const UniverseObjectVisitor& visitor) const
{
    ObjectIDVec retval;
    for (ObjectMap::const_iterator it = m_objects.begin(); it != m_objects.end(); ++it) {
        if (it->second->Accept(visitor))
            retval.push_back(it->first);
    }
    return retval;
}

Universe::iterator Universe::begin()
{ return m_objects.begin(); }

Universe::iterator Universe::end()
{ return m_objects.end(); }

Universe::const_iterator Universe::begin() const
{ return m_objects.begin(); }

Universe::const_iterator Universe::end() const
{ return m_objects.end(); }

const UniverseObject* Universe::DestroyedObject(int id) const
{
    const_iterator it = m_destroyed_objects.find(id);
    return (it != m_destroyed_objects.end() ? it->second : 0);
}

const ShipDesign* Universe::GetShipDesign(int ship_design_id) const
{
    ship_design_iterator it = m_ship_designs.find(ship_design_id);
    return (it != m_ship_designs.end() ? it->second : 0);
}

double Universe::LinearDistance(int system1_id, int system2_id) const
{
    int system1_index = SystemGraphIndex(m_system_graph, system1_id);
    int system2_index = SystemGraphIndex(m_system_graph, system2_id);
    return m_system_distances.at(std::max(system1_index, system2_index)).at(std::min(system1_index, system2_index));
}

std::pair<std::list<System*>, double> Universe::ShortestPath(int system1_id, int system2_id, int empire_id/* = ALL_EMPIRES*/) const
{
    double linear_distance = LinearDistance(system1_id, system2_id);
    if (empire_id == ALL_EMPIRES) {
        return ShortestPathImpl(m_system_graph, system1_id, system2_id, linear_distance);
    } else {
        EmpireViewSystemGraphMap::const_iterator graph_it = m_empire_system_graph_views.find(empire_id);
        if (graph_it != m_empire_system_graph_views.end())
            return ShortestPathImpl(*graph_it->second, system1_id, system2_id, linear_distance);
    }
    return std::pair<std::list<System*>, double>();
}

std::pair<std::list<System*>, int> Universe::LeastJumpsPath(int system1_id, int system2_id, int empire_id/* = ALL_EMPIRES*/) const
{
    if (empire_id == ALL_EMPIRES) {
        return LeastJumpsPathImpl(m_system_graph, system1_id, system2_id);
    } else {
        EmpireViewSystemGraphMap::const_iterator graph_it = m_empire_system_graph_views.find(empire_id);
        if (graph_it != m_empire_system_graph_views.end())
            return LeastJumpsPathImpl(*graph_it->second, system1_id, system2_id);
    }
    return std::pair<std::list<System*>, int>();
}

bool Universe::SystemsConnected(int system1_id, int system2_id, int empire_id) const
{
    std::pair<std::list<System*>, int> path = LeastJumpsPath(system1_id, system2_id, empire_id);
    return (!path.first.empty());
}

bool Universe::SystemReachable(int system_id, int empire_id) const
{
    if (empire_id == ALL_EMPIRES) {
        return SystemReachableImpl(m_system_graph, system_id);
    } else {
        EmpireViewSystemGraphMap::const_iterator graph_it = m_empire_system_graph_views.find(empire_id);
        if (graph_it != m_empire_system_graph_views.end())
            return SystemReachableImpl(*graph_it->second, system_id);
    }
    return false;
}

std::map<double, System*> Universe::ImmediateNeighbors(int system_id, int empire_id/* = ALL_EMPIRES*/) const
{
    if (empire_id == ALL_EMPIRES) {
        return ImmediateNeighborsImpl(m_system_graph, system_id);
    } else {
        EmpireViewSystemGraphMap::const_iterator graph_it = m_empire_system_graph_views.find(empire_id);
        if (graph_it != m_empire_system_graph_views.end())
            return ImmediateNeighborsImpl(*graph_it->second, system_id);
    }
    return std::map<double, System*>();
}

int Universe::Insert(UniverseObject* obj)
{
    int retval = UniverseObject::INVALID_OBJECT_ID;
    if (obj) {
        if (m_last_allocated_object_id + 1 < UniverseObject::MAX_ID) {
            m_objects[++m_last_allocated_object_id] = obj;
            obj->SetID(m_last_allocated_object_id);
            retval = m_last_allocated_object_id;
        } else { // we'll probably never execute this branch, considering how many IDs are available
            // find a hole in the assigned IDs in which to place the object
            int last_id_seen = UniverseObject::INVALID_OBJECT_ID;
            for (ObjectMap::iterator it = m_objects.begin(); it != m_objects.end(); ++it) {
                if (1 < it->first - last_id_seen) {
                    m_objects[last_id_seen + 1] = obj;
                    obj->SetID(last_id_seen + 1);
                    retval = last_id_seen + 1;
                    break;
                }
            }
        }
    }
    return retval;
}

bool Universe::InsertID(UniverseObject* obj, int id )
{
    bool retval = false;

    if (obj) {
        if ( id < UniverseObject::MAX_ID) {
            m_objects[id] = obj;
            obj->SetID(id);
            retval = true;
        }
    }
    return retval;
}

int Universe::InsertShipDesign(ShipDesign* ship_design)
{
    int retval = UniverseObject::INVALID_OBJECT_ID;
    if (ship_design) {
        if (m_last_allocated_design_id + 1 < UniverseObject::MAX_ID) {
            m_ship_designs[++m_last_allocated_design_id] = ship_design;
            retval = m_last_allocated_design_id;
        } else { // we'll probably never execute this branch, considering how many IDs are available
            // find a hole in the assigned IDs in which to place the object
            int last_id_seen = UniverseObject::INVALID_OBJECT_ID;
            for (ShipDesignMap::iterator it = m_ship_designs.begin(); it != m_ship_designs.end(); ++it) {
                if (1 < it->first - last_id_seen) {
                    m_ship_designs[last_id_seen + 1] = ship_design;
                    retval = last_id_seen + 1;
                    break;
                }
            }
        }
    }
    return retval;
}

bool Universe::InsertShipDesignID(ShipDesign* ship_design, int id)
{
    bool retval = false;

    if (ship_design) {
        if (id < UniverseObject::MAX_ID) {
            ship_design->SetID(id);
            m_ship_designs[id] = ship_design;
            retval = true;
        }
    }
    return retval;
}

void Universe::InitMeterEstimatesAndDiscrepancies()
{
    // clear old discrepancies
    m_effect_discrepancy_map.clear();

    // generate new estimates (normally uses discrepancies, but in this case will find none)
    UpdateMeterEstimates();

    // determine meter max discrepancies
    for (EffectAccountingMap::iterator obj_it = m_effect_accounting_map.begin(); obj_it != m_effect_accounting_map.end(); ++obj_it) {
        UniverseObject* obj = Object(obj_it->first);    // object that has some meters
        std::map<MeterType, std::vector<EffectAccountingInfo> >& meters_map = obj_it->second;

        // every meter has a value at the start of the turn, and a value after updating with known effects
        for (std::map<MeterType, std::vector<EffectAccountingInfo> >::iterator meter_type_it = meters_map.begin(); meter_type_it != meters_map.end(); ++meter_type_it) {
            MeterType type = meter_type_it->first;
            Meter* meter = obj->GetMeter(type);
            assert(meter);  // all objects should only have accounting info for a meter if that meter exists
            int object_id = obj->ID();

            // discrepancy is the difference between expected and actual meter values at start of turn
            double discrepancy = meter->InitialMax() - meter->Max();

            if (discrepancy == 0.0) continue;   // no discrepancy for this meter

            // add to discrepancy map
            m_effect_discrepancy_map[object_id][type] = discrepancy;

            // correct current max meter estimate for discrepancy
            meter->AdjustMax(discrepancy);

            // add discrepancy adjustment to meter accounting
            EffectAccountingInfo info;
            info.cause_type = ECT_UNKNOWN_CAUSE;
            info.meter_change = discrepancy;
            info.running_meter_total = meter->Max();
            
            m_effect_accounting_map[object_id][type].push_back(info);
        }
    }
}

void Universe::UpdateMeterEstimates()
{
    m_effect_accounting_map.clear();

    // for all objects to see if they have meters that need to be processed
    for (iterator obj_it = begin(); obj_it != end(); ++obj_it) {
        UniverseObject* obj = obj_it->second;
        int object_id = obj_it->first;

        // Reset max meters to METER_MIN
        obj->ResetMaxMeters();

        // Apply non-effect focus mods from tables
        obj->ApplyUniverseTableMaxMeterAdjustments();

        // record value of max meters after applying universe table adjustments
        for (MeterType type = MeterType(0); type != NUM_METER_TYPES; type = MeterType(type + 1)) {
            Meter* meter = obj->GetMeter(type);
            if (meter) {
                EffectAccountingInfo info;
                info.source_id = UniverseObject::INVALID_OBJECT_ID;
                info.caused_by_empire_id = -1;
                info.cause_type = ECT_UNIVERSE_TABLE_ADJUSTMENT;
                info.meter_change = meter->Max() - Meter::METER_MIN;
                info.running_meter_total = meter->Max();
                
                m_effect_accounting_map[object_id][type].push_back(info);
            }
        }

        // reset current meters to value at star of turn (before growth or effects changes)
    }

    // cache all activation and scoping condition results before applying Effects, since the application of
    // these Effects may affect the activation and scoping evaluations
    EffectsAndTargetsMap effects_targets_map;
    EffectsAndCausesMap effects_causes_map;
    GetEffectsAndTargets(effects_targets_map, &effects_causes_map);

    // Apply and record effect meter adjustments
    ExecuteMeterEffects(effects_targets_map, &effects_causes_map);

    // Apply known discrepancies between expected and calculated meter maxes at start of turn.  This
    // accounts for the unknown effects on the meter, and brings the estimate in line with the actual
    // max at the start of the turn
    if (!m_effect_discrepancy_map.empty()) {
        for (iterator obj_it = begin(); obj_it != end(); ++obj_it) {
            UniverseObject* obj = obj_it->second;
            int object_id = obj_it->first;

            // check if this object has any discrepancies
            EffectDiscrepancyMap::iterator dis_it = m_effect_discrepancy_map.find(object_id);
            if (dis_it == m_effect_discrepancy_map.end()) continue;

            // apply all meters' discrapancies
            std::map<MeterType, double>& meter_map = dis_it->second;
            for(std::map<MeterType, double>::iterator meter_it = meter_map.begin(); meter_it != meter_map.end(); ++meter_it) {
                MeterType type = meter_it->first;
                double discrepancy = meter_it->second;

                //if (discrepancy == 0.0) continue;

                Meter* meter = obj->GetMeter(type);

                if (meter) {
                    Logger().debugStream() << "object " << object_id << " has meter " << type << " discrepancy: " << discrepancy << " and final max: " << meter->Max();

                    meter->AdjustMax(discrepancy);

                    EffectAccountingInfo info;
                    info.cause_type = ECT_UNKNOWN_CAUSE;
                    info.meter_change = discrepancy;
                    info.running_meter_total = meter->Max();
                    
                    m_effect_accounting_map[object_id][type].push_back(info);
                }
            }
        }
    }

    ///////////////////////////
    // do current meter growth ?
    ///////////////////////////
}

void Universe::GetEffectsAndTargets(EffectsAndTargetsMap& effects_targets_map, EffectsAndCausesMap* effects_causes_map)
{
    effects_targets_map.clear();
    if (effects_causes_map)
        effects_causes_map->clear();

    // get effects groups from specials
    for (Universe::const_iterator it = begin(); it != end(); ++it) {
        for (std::set<std::string>::const_iterator special_it = it->second->Specials().begin();
             special_it != it->second->Specials().end();
             ++special_it) {
            const Special* special = GetSpecial(*special_it);
            assert(special);
            for (unsigned int i = 0; i < special->Effects().size(); ++i) {
                boost::shared_ptr<const Effect::EffectsGroup> effect = special->Effects()[i];
                EffectsAndTargetsMapElem map_elem(effect, std::make_pair(it->first, Effect::EffectsGroup::TargetSet()));
                special->Effects()[i]->GetTargetSet(it->first, map_elem.second.second);
                effects_targets_map.insert(map_elem);
                if (effects_causes_map)
                    effects_causes_map->insert(EffectsAndCausesMapElem(effect, std::make_pair(it->first, std::make_pair(ECT_SPECIAL, special->Name()))));
            }
        }
    }

    // get effects groups from techs
    for (EmpireManager::iterator it = Empires().begin(); it != Empires().end(); ++it) {
        for (Empire::TechItr tech_it = it->second->TechBegin(); tech_it != it->second->TechEnd(); ++tech_it) {
            const Tech* tech = GetTech(*tech_it);
            assert(tech);
            for (unsigned int i = 0; i < tech->Effects().size(); ++i) {
                boost::shared_ptr<const Effect::EffectsGroup> effect = tech->Effects()[i];
                EffectsAndTargetsMapElem map_elem(effect, std::make_pair(it->second->CapitolID(), Effect::EffectsGroup::TargetSet()));
                tech->Effects()[i]->GetTargetSet(it->second->CapitolID(), map_elem.second.second);
                effects_targets_map.insert(map_elem);
                if (effects_causes_map)
                    effects_causes_map->insert(EffectsAndCausesMapElem(effect, std::make_pair(it->second->CapitolID(), std::make_pair(ECT_TECH, tech->Name()))));
            }
        }
    }

    // get effects groups from buildings
    std::vector<Building*> buildings = FindObjects<Building>();
    for (unsigned int i = 0; i < buildings.size(); ++i) {
        const BuildingType* building_type = buildings[i]->GetBuildingType();
        assert(building_type);
        for (unsigned int j = 0; j < building_type->Effects().size(); ++j) {
            boost::shared_ptr<const Effect::EffectsGroup> effect = building_type->Effects()[j];
            EffectsAndTargetsMapElem map_elem(effect, std::make_pair(buildings[i]->ID(), Effect::EffectsGroup::TargetSet()));
            building_type->Effects()[j]->GetTargetSet(buildings[i]->ID(), map_elem.second.second);
            effects_targets_map.insert(map_elem);
            if (effects_causes_map)
                effects_causes_map->insert(EffectsAndCausesMapElem(effect, std::make_pair(buildings[i]->ID(), std::make_pair(ECT_BUILDING, building_type->Name()))));
        }
    }
}

void Universe::ExecuteEffects(EffectsAndTargetsMap& effects_targets_map)
{
    std::map<std::string, Effect::EffectsGroup::TargetSet> executed_nonstacking_effects;

    for (EffectsAndTargetsMap::const_iterator it = effects_targets_map.begin(); it != effects_targets_map.end(); ++it) {
        // if other EffectsGroups with the same stacking group have affected some of the targets in the scope of the current EffectsGroup, skip them
        std::map<std::string, std::set<UniverseObject*> >::iterator non_stacking_it = executed_nonstacking_effects.find(it->first->StackingGroup());
        Effect::EffectsGroup::TargetSet targets(it->second.second);
        if (non_stacking_it != executed_nonstacking_effects.end()) {
            for (Effect::EffectsGroup::TargetSet::const_iterator object_it = non_stacking_it->second.begin(); object_it != non_stacking_it->second.end(); ++object_it) {
                targets.erase(*object_it);
            }
        }

        // execute the Effects in the EffectsGroup
        it->first->Execute(it->second.first, targets);

        // if this EffectsGroup belongs to a stacking group, add the objects just affected by it to executed_nonstacking_effects
        if (it->first->StackingGroup() != "") {
            Effect::EffectsGroup::TargetSet& affected_targets = executed_nonstacking_effects[it->first->StackingGroup()];
            for (Effect::EffectsGroup::TargetSet::const_iterator object_it = targets.begin(); object_it != targets.end(); ++object_it) {
                affected_targets.insert(*object_it);
            }
        }
    }

    for (std::set<int>::iterator it = m_marked_destroyed.begin(); it != m_marked_destroyed.end(); ++it) {
        DestroyImpl(*it);
    }
}

void Universe::ExecuteMeterEffects(EffectsAndTargetsMap& effects_targets_map, EffectsAndCausesMap* effects_causes_map)
{
    if (effects_causes_map)
        assert(effects_targets_map.size() == effects_causes_map->size());

    std::map<std::string, Effect::EffectsGroup::TargetSet> executed_nonstacking_effects;

    EffectsAndCausesMap::const_iterator causes_it;

    for (EffectsAndTargetsMap::const_iterator targets_it = effects_targets_map.begin(); targets_it != effects_targets_map.end(); ++targets_it) {
        Effect::EffectsGroup::TargetSet targets = targets_it->second.second;
        const boost::shared_ptr<const Effect::EffectsGroup>& effects_group = targets_it->first;

        // if other EffectsGroups with the same stacking group have affected some of the targets in the scope of the current EffectsGroup, skip them
        std::map<std::string, std::set<UniverseObject*> >::iterator non_stacking_it = executed_nonstacking_effects.find(targets_it->first->StackingGroup());
        if (non_stacking_it != executed_nonstacking_effects.end()) {
            for (Effect::EffectsGroup::TargetSet::const_iterator object_it = non_stacking_it->second.begin(); object_it != non_stacking_it->second.end(); ++object_it) {
                targets.erase(*object_it);
            }
        }

        // if doing effect accounting, get cause of effect
        EffectsCauseType cause_type = INVALID_EFFECTS_GROUP_CAUSE_TYPE;
        std::string specific_cause = "";
        if (effects_causes_map) {
            causes_it = effects_causes_map->find(effects_group);
            if (causes_it == effects_causes_map->end())
                Logger().debugStream() << "something funky's going on...";
            cause_type = causes_it->second.second.first;        // see definition of Universe::EffectsAndCausesMapElem
            specific_cause = causes_it->second.second.second;
        }

        // execute only the SetMeter effects in the EffectsGroup
        int source = targets_it->second.first;
        const std::vector<Effect::EffectBase*>& effects = effects_group->EffectsList();
        for (unsigned int i = 0; i < effects.size(); ++i) {
            const Effect::SetMeter* meter_effect = dynamic_cast<Effect::SetMeter*>(effects[i]);
            if (!meter_effect) continue;

            // do effect accounting
            if (effects_causes_map) {
                // determine meter to be altered by this effect
                MeterType meter_type = meter_effect->GetMeterType();
                
                // record pre-effect meter values
                for (Effect::EffectsGroup::TargetSet::iterator target_it = targets.begin(); target_it != targets.end(); ++target_it) {
                    UniverseObject* target = *target_it;
                    const Meter* meter = target->GetMeter(meter_type);
                    if (!meter) continue;   // some objects might match target conditions, but not actually have the relevant meter

                    // create new accounting info for this effect on this target/meter
                    EffectAccountingInfo info;
                    info.source_id = source;
                    info.cause_type = ECT_UNKNOWN_CAUSE;    // need to get this somehow ...
                    info.specific_cause = "";               // ... and this.
                    info.running_meter_total = meter->Max();    // using as temp storage for max value before effects are applied
                    
                    // add accounting for this effect to end of vector
                    m_effect_accounting_map[target->ID()][meter_type].push_back(info);
                }

                // apply effect to targets
                effects_group->Execute(source, targets, i);

                // find change in meter due to effect: equal to post-meter minus pre-meter value
                for (Effect::EffectsGroup::TargetSet::iterator target_it = targets.begin(); target_it != targets.end(); ++target_it) {
                    UniverseObject* target = *target_it;
                    const Meter* meter = target->GetMeter(meter_type);
                    if (!meter) continue;   // some objects might match target conditions, but not actually have the relevant meter

                    // retreive info for this effect
                    EffectAccountingInfo& info = m_effect_accounting_map[target->ID()][meter_type].back();

                    // update accounting info with meter change and new total
                    info.meter_change = meter->Max() - info.running_meter_total;    // change is new max minus old max (stored in temp value with misleading name)
                    info.running_meter_total = meter->Max();        // replacing temp stored value with new meter total
                    info.cause_type = cause_type;
                    info.specific_cause = specific_cause;
                }

            } else {                
                // just apply effect
                effects_group->Execute(source, targets, i);
            }
        }

        // if this EffectsGroup belongs to a stacking group, add the objects just affected by it to executed_nonstacking_effects
        if (targets_it->first->StackingGroup() != "") {
            Effect::EffectsGroup::TargetSet& affected_targets = executed_nonstacking_effects[targets_it->first->StackingGroup()];
            for (Effect::EffectsGroup::TargetSet::const_iterator object_it = targets.begin(); object_it != targets.end(); ++object_it) {
                affected_targets.insert(*object_it);
            }
        }

        if (effects_causes_map)
            ++causes_it;
    }
}

void Universe::ApplyEffects()
{
    m_marked_destroyed.clear();

    // cache all activation and scoping condition results before applying Effects, since the application of
    // these Effects may affect the activation and scoping evaluations
    EffectsAndTargetsMap effects_targets_map;
    GetEffectsAndTargets(effects_targets_map);

    // reset max meter state that is affected by the application of effects
    for (const_iterator it = begin(); it != end(); ++it) {
        it->second->ResetMaxMeters();
        it->second->ApplyUniverseTableMaxMeterAdjustments();
    }

    ExecuteEffects(effects_targets_map);
}

void Universe::RebuildEmpireViewSystemGraphs()
{
    m_empire_system_graph_views.clear();
    for (EmpireManager::const_iterator it = Empires().begin(); it != Empires().end(); ++it) {
        EdgeVisibilityFilter filter(&m_system_graph, it->first);
        boost::shared_ptr<EmpireViewSystemGraph> filtered_graph_ptr(new EmpireViewSystemGraph(m_system_graph, filter));
        m_empire_system_graph_views[it->first] = filtered_graph_ptr;
    }
}

void Universe::Destroy(int id)
{
    s_inhibit_universe_object_signals = true;

    UniverseObject* obj;
    iterator it = m_objects.find(id);

    // remove object from any containing UniverseObject
    if (it != m_objects.end()) {
        obj = it->second;
        Logger().debugStream() << "Destroying object : " << id << " : " << obj->Name();

        // get and record set of empires that can presently see this object
        std::set<int> knowing_empires;
        for (EmpireManager::iterator emp_it = Empires().begin(); emp_it != Empires().end(); ++emp_it) {
            int empire_id = emp_it->first;
            if (obj->GetVisibility(empire_id) != UniverseObject::NO_VISIBILITY || universe_object_cast<System*>(obj)) {
                knowing_empires.insert(empire_id);
                Logger().debugStream() << "..visible to empire: " << empire_id;
            }
        }
        m_destroyed_object_knowers[id] = knowing_empires;

        // remove object from any containing objects
        if (System* sys = obj->GetSystem())
            sys->Remove(id);
        if (Ship* ship = universe_object_cast<Ship*>(obj)) {
            if (Fleet* fleet = ship->GetFleet())
                fleet->RemoveShip(ship->ID());
        } else if (Building* building = universe_object_cast<Building*>(obj)) {
            if (Planet* planet = building->GetPlanet())
                planet->RemoveBuilding(building->ID());
        }

        // remove from existing objects set and insert into destroyed objects set
        m_objects.erase(id);
        m_destroyed_objects[id] = obj;
    } else {
        Logger().debugStream() << "Universe::Destroy called for nonexistant object with id: " << id;
    }

    s_inhibit_universe_object_signals = false;
}

bool Universe::Delete(int id)
{
    s_inhibit_universe_object_signals = true;

    // find object amongst existing objects
    UniverseObject* obj;
    iterator it = m_objects.find(id);
    if (it != m_objects.end()) {
        obj = it->second;

        // remove object from any containing UniverseObject
        if (System* sys = obj->GetSystem())
            sys->Remove(id);
        if (Ship* ship = universe_object_cast<Ship*>(obj)) {
            if (Fleet* fleet = ship->GetFleet())
                fleet->RemoveShip(ship->ID());
        } else if (Building* building = universe_object_cast<Building*>(obj)) {
            if (Planet* planet = building->GetPlanet())
                planet->RemoveBuilding(building->ID());
        }

        m_objects.erase(id);
        UniverseObjectDeleteSignal(obj);
        delete obj;
        s_inhibit_universe_object_signals = false;
        return true;
    }

    // find object amongst destroyed objects
    it = m_destroyed_objects.find(id);
    if (it != m_destroyed_objects.end()) {
        obj = it->second;
        m_destroyed_objects.erase(id);
        UniverseObjectDeleteSignal(obj);
        delete obj;
        s_inhibit_universe_object_signals = false;
        return true;
    }

    Logger().debugStream() << "Tried to delete a nonexistant objects with id: " << id;

    s_inhibit_universe_object_signals = false;
    return false;
}

void Universe::EffectDestroy(int id)
{
    m_marked_destroyed.insert(id);
}

void Universe::HandleEmpireElimination(int empire_id)
{
    for (EffectAccountingMap::iterator obj_it = m_effect_accounting_map.begin(); obj_it != m_effect_accounting_map.end(); ++obj_it) {
        // ever meter has a value at the start of the turn, and a value after updating with known effects
        for (std::map<MeterType, std::vector<EffectAccountingInfo> >::iterator meter_type_it = obj_it->second.begin(); meter_type_it != obj_it->second.end(); ++meter_type_it) {
            for (std::size_t i = 0; i < meter_type_it->second.size(); ) {
                if (meter_type_it->second[i].caused_by_empire_id == empire_id)
                    meter_type_it->second.erase(meter_type_it->second.begin() + i);
                else
                    ++i;
            }
        }
    }
}

bool Universe::ConnectedWithin(int system1, int system2, int maxLaneJumps, std::vector<std::set<int> >& laneSetArray) {
    // list of indices of systems that are accessible from previously visited systems.
    // when a new system is found to be accessible, it is added to the back of the
    // list.  the list is iterated through from front to back to find systems
    // to examine
    std::list<int> accessibleSystemsList;
    std::list<int>::iterator sysListIter, sysListEnd;
    
    // map using star index number as the key, and also storing the number of starlane
    // jumps away from system1 a given system is.  this is used to determine if a
    // system has already been added to the accessibleSystemsList without needing
    // to iterate through the list.  it also provides some indication of the
    // current depth of the search, which allows the serch to terminate after searching
    // to the depth of maxLaneJumps without finding system2
    // (considered using a vector for this, but felt that for large galaxies, the
    // size of the vector and the time to intialize would be too much)
    std::map<int, int> accessibleSystemsMap;

    // system currently being investigated, destination of a starlane origination at curSys
    int curSys, curLaneDest;
    // "depth" level in tree of system currently being investigated
    int curDepth;

    // iterators to set of starlanes, in graph, for the current system    
    std::set<int>::iterator curSysLanesSetIter, curSysLanesSetEnd;
    
    // check for simple cases for quick termination
    if (system1 == system2) return true; // system is always connected to itself
    if (0 == maxLaneJumps) return false; // no system is connected to any other system by less than 1 jump
    if (0 == (laneSetArray[system1]).size()) return false; // no lanes out of start system
    if (0 == (laneSetArray[system2]).size()) return false; // no lanes into destination system
    if (system1 >= static_cast<int>(laneSetArray.size()) || system2 >= static_cast<int>(laneSetArray.size())) return false; // out of range
    if (system1 < 0 || system2 < 0) return false; // out of range
    
    // add starting system to list and set of accessible systems
    accessibleSystemsList.push_back(system1);
    accessibleSystemsMap.insert(std::pair<int, int>(system1, 0));

    // loop through visited systems
    sysListIter = accessibleSystemsList.begin();
    sysListEnd = accessibleSystemsList.end();
    while (sysListIter != sysListEnd) {
        curSys = *sysListIter;
        
        // check that iteration hasn't reached maxLaneJumps levels deep, which would 
        // mean that system2 isn't within maxLaneJumps starlane jumps of system1
        curDepth = (*accessibleSystemsMap.find(curSys)).second;

        if (curDepth >= maxLaneJumps) return false;
        
        // get set of starlanes for this system
        curSysLanesSetIter = (laneSetArray[curSys]).begin();
        curSysLanesSetEnd = (laneSetArray[curSys]).end();
        
        // add starlanes accessible from this system to list and set of accessible starlanes
        // (and check for the goal starlane)
        while (curSysLanesSetIter != curSysLanesSetEnd) {
            curLaneDest = *curSysLanesSetIter;
        
            // check if curLaneDest has been added to the map of accessible systems
            if (0 == accessibleSystemsMap.count(curLaneDest)) {
                
                // check for goal
                if (curLaneDest == system2) return true;
                
                // add curLaneDest to accessible systems list and map
                accessibleSystemsList.push_back(curLaneDest);
                accessibleSystemsMap.insert(std::pair<int, int>(curLaneDest, curDepth + 1));
               }
        
            curSysLanesSetIter++;
        }

        sysListIter++;
    }    
    return false; // default
}

void Universe::InitializeSystemGraph()
{
    for (int i = static_cast<int>(boost::num_vertices(m_system_graph)) - 1; i >= 0; --i) {
        boost::clear_vertex(i, m_system_graph);
        boost::remove_vertex(i, m_system_graph);
    }

    std::vector<System*> systems = FindObjects<System>();
    m_system_distances.resize(systems.size());
    SystemPointerPropertyMap pointer_property_map = boost::get(vertex_system_pointer_t(), m_system_graph);

    EdgeWeightPropertyMap edge_weight_map = boost::get(boost::edge_weight, m_system_graph);
    typedef boost::graph_traits<SystemGraph>::edge_descriptor EdgeDescriptor;

    std::map<int, int> system_id_graph_index_reverse_lookup_map;    // key is system ID, value is index in m_system_graph of system's vertex

    for (int i = 0; i < static_cast<int>(systems.size()); ++i) {
        // add a vertex to the graph for this system, and assign it a pointer for its System object
        boost::add_vertex(m_system_graph);
        System* system1 = systems[i];
        pointer_property_map[i] = system1;
        // add record of index in m_system_graph of this system
        system_id_graph_index_reverse_lookup_map[system1->ID()] = i;
    }

    for (int i = 0; i < static_cast<int>(systems.size()); ++i) {
        System* system1 = systems[i];

        // add edges and edge weights
        for (System::lane_iterator it = system1->begin_lanes(); it != system1->end_lanes(); ++it) {
            // get id in universe of system at other end of lane
            int lane_dest_id = it->first;

            // get m_system_graph index for this system
            int lane_dest_graph_index = system_id_graph_index_reverse_lookup_map[lane_dest_id];

            std::pair<EdgeDescriptor, bool> add_edge_result = boost::add_edge(i, lane_dest_graph_index, m_system_graph);
            
            if (it->second) {                               // if this is a wormhole
                edge_weight_map[add_edge_result.first] = 0.0;
            } else if (add_edge_result.second) {            // if this is a non-duplicate starlane
                UniverseObject* system2 = Object(it->first);
                double x_dist = system2->X() - system1->X();
                double y_dist = system2->Y() - system1->Y();
                edge_weight_map[add_edge_result.first] = std::sqrt(x_dist * x_dist + y_dist * y_dist);
            }
        }

        // define the straight-line system distances for this system
        m_system_distances[i].clear();
        for (int j = 0; j < i; ++j) {
            UniverseObject* system2 = Object(j);
            double x_dist = system2->X() - system1->X();
            double y_dist = system2->Y() - system1->Y();
            m_system_distances[i].push_back(std::sqrt(x_dist * x_dist + y_dist * y_dist));
        }
        m_system_distances[i].push_back(0.0);
    }

    RebuildEmpireViewSystemGraphs();
}

double Universe::UniverseWidth()
{
    return s_universe_width;
}

const bool& Universe::UniverseObjectSignalsInhibited()
{
    return s_inhibit_universe_object_signals;
}

void Universe::InhibitUniverseObjectSignals(bool inhibit)
{
    s_inhibit_universe_object_signals = inhibit;
}

void Universe::DestroyImpl(int id)
{
    UniverseObject* obj = Object(id);
    if (!obj)
        return;
    if (Ship* ship = universe_object_cast<Ship*>(obj)) {
        // if a ship is being deleted, and it is the last ship in its fleet, then the empty fleet should also be deleted
        Fleet* fleet = ship->GetFleet();
        Delete(id);
        if (fleet && fleet->NumShips() == 0)
            Delete(fleet->ID());
    } else if (Fleet* fleet = universe_object_cast<Fleet*>(obj)) {
        for (Fleet::iterator it = fleet->begin(); it != fleet->end(); ++it) {
            Delete(*it);
        }
        Delete(id);
    } else if (Planet* planet = universe_object_cast<Planet*>(obj)) {
        for (std::set<int>::const_iterator it = planet->Buildings().begin(); it != planet->Buildings().end(); ++it) {
            Delete (*it);
        }
        Delete(id);
    } else if (universe_object_cast<System*>(obj)) {
        // unsupported: do nothing
    } else {
        Delete(id);
    }
}

void Universe::GetShipDesignsToSerialize(const ObjectMap& serialized_objects, ShipDesignMap& designs_to_serialize)
{
    if (s_encoding_empire == ALL_EMPIRES) {
        designs_to_serialize = m_ship_designs;
    } else {
        // add all ship designs of ships this empire knows about -> "objects" from above, not "m_objects"
        for (ObjectMap::const_iterator it = serialized_objects.begin(); it != serialized_objects.end(); ++it) {
            Ship* ship = universe_object_cast<Ship*>(it->second);
            if (ship) {
                int design_id = ship->DesignID();
                if (design_id != UniverseObject::INVALID_OBJECT_ID)
                    designs_to_serialize[design_id] = m_ship_designs[design_id];
            }
        }

        // add all ship designs owned by this empire
        Empire* empire = Empires().Lookup(s_encoding_empire);
        for (Empire::ShipDesignItr it = empire->ShipDesignBegin(); it != empire->ShipDesignEnd(); ++it) {
            designs_to_serialize[*it] = m_ship_designs[*it];
        }
    }
}

//////////////////////////////////////////
//    Server-Only General Functions     //
//////////////////////////////////////////
int Universe::GenerateObjectID()
{
#ifdef FREEORION_BUILD_SERVER
    return ++m_last_allocated_object_id;
#else
    throw std::runtime_error("Non-server called Universe::GenerateObjectID");
#endif
}

int Universe::GenerateDesignID()
{
#ifdef FREEORION_BUILD_SERVER
    return ++m_last_allocated_design_id;
#else
    throw std::runtime_error("Non-server called Universe::GenerateDesignID");
#endif
}


//////////////////////////////////////////
//  Server-Only Galaxy Setup Functions  //
//////////////////////////////////////////
namespace {
#ifdef FREEORION_BUILD_SERVER
    const double  MIN_SYSTEM_SEPARATION = 30.0; // in universe units [0.0, s_universe_width]
    const double  MIN_HOME_SYSTEM_SEPARATION = 200.0; // in universe units [0.0, s_universe_width]
    const double  AVG_UNIVERSE_WIDTH = 1000.0 / std::sqrt(150.0); // so a 150 star universe is 1000 units across
    const int     ADJACENCY_BOXES = 25;
    const double  PI = 3.141592653589793;
    const int     MAX_SYSTEM_ORBITS = 10;   // maximum slots where planets can be, in v0.2
    SmallIntDistType g_hundred_dist = SmallIntDist(1, 100); // a linear distribution [1, 100] used in most universe generation
    const int MAX_ATTEMPTS_PLACE_SYSTEM = 100;
#endif

    double CalcNewPosNearestNeighbour(const std::pair<double, double> &position,const std::vector<std::pair<double, double> > &positions)
    {
#ifdef FREEORION_BUILD_SERVER
        if(positions.size()==0)
            return 0.0;

        unsigned int j;
        double lowest_dist=  (positions[0].first  - position.first ) * (positions[0].first  - position.first ) 
            + (positions[0].second - position.second) * (positions[0].second - position.second),distance=0.0;

        for (j=1; j < positions.size(); ++j){
            distance =  (positions[j].first  - position.first ) * (positions[j].first  - position.first ) 
                + (positions[j].second - position.second) * (positions[j].second - position.second);
            if(lowest_dist>distance)
                lowest_dist = distance;
        }
        return lowest_dist;
#else
        throw std::runtime_error("Non-server called CalcNewPosNearestNeighbour; only server should call this while creating the universe");
#endif
    }

    void SpiralGalaxyCalcPositions(std::vector<std::pair<double, double> > &positions, unsigned int arms, unsigned int stars, double width, double height)
    {
#ifdef FREEORION_BUILD_SERVER
        double arm_offset     = RandDouble(0.0,2.0*PI);
        double arm_angle      = 2.0*PI / arms;
        double arm_spread     = 0.3 * PI / arms;
        double arm_length     = 1.5 * PI;
        double center         = 0.25;
        double x,y;

        int i, attempts;

        GaussianDistType  random_gaussian = GaussianDist(0.0,arm_spread);
        SmallIntDistType  random_arm      = SmallIntDist(0  ,arms);
        DoubleDistType    random_angle    = DoubleDist  (0.0,2.0*PI);
        DoubleDistType    random_radius   = DoubleDist  (0.0,  1.0);

        for (i = 0, attempts = 0; i < static_cast<int>(stars) && attempts < MAX_ATTEMPTS_PLACE_SYSTEM; ++i, ++attempts)
        {
            double radius = random_radius();

            if (radius < center) {
                double angle = random_angle();
                x = radius * cos( arm_offset + angle );
                y = radius * sin( arm_offset + angle );
            } else {
                double arm    = (double)random_arm() * arm_angle;
                double angle  = random_gaussian();

                x = radius * cos( arm_offset + arm + angle + radius * arm_length );
                y = radius * sin( arm_offset + arm + angle + radius * arm_length );
            }

            x = (x + 1) * width / 2.0;
            y = (y + 1) * height / 2.0;

            if (x < 0 || width <= x || y < 0 || height <= y)
                continue;

            // See if new star is too close to any existing star.
            double lowest_dist=CalcNewPosNearestNeighbour(std::pair<double,double>(x,y),positions);

            // If so, we try again.
            if (lowest_dist < MIN_SYSTEM_SEPARATION * MIN_SYSTEM_SEPARATION && attempts < MAX_ATTEMPTS_PLACE_SYSTEM - 1) {
                --i;
                continue;
            }

            // Add the new star location.
            positions.push_back(std::make_pair(x, y));

            // Note that attempts is reset for every star.
            attempts = 0;
        }
#else
        throw std::runtime_error("Non-server called SpiralGalaxyCalcPositions; only server should call this while creating the universe");
#endif
    }

    void EllipticalGalaxyCalcPositions(std::vector<std::pair<double,double> > &positions, unsigned int stars, double width, double height)
    {
#ifdef FREEORION_BUILD_SERVER
        const double ellipse_width_vs_height = RandDouble(0.4, 0.6);
        const double rotation = RandDouble(0.0, PI),
            rotation_sin = std::sin(rotation),
            rotation_cos = std::cos(rotation);
        const double gap_constant = .95;
        const double gap_size = 1.0 - gap_constant * gap_constant * gap_constant;

        // Random number generators.
        DoubleDistType radius_dist = DoubleDist(0.0, gap_constant);
        DoubleDistType random_angle  = DoubleDist(0.0, 2.0 * PI);

        // Used to give up when failing to place a star too often.
        int attempts = 0;

        // For each attempt to place a star...
        for (unsigned int i = 0; i < stars && attempts < MAX_ATTEMPTS_PLACE_SYSTEM; ++i, ++attempts){
            double radius = radius_dist();
            // Adjust for bigger density near center and create gap.
            radius = radius * radius * radius + gap_size;
            double angle  = random_angle();

            // Rotate for individual angle and apply elliptical shape.
            double x1 = radius * std::cos(angle);
            double y1 = radius * std::sin(angle) * ellipse_width_vs_height;

            // Rotate for ellipse angle.
            double x = x1 * rotation_cos - y1 * rotation_sin;
            double y = x1 * rotation_sin + y1 * rotation_cos;

            // Move from [-1.0, 1.0] universe coordinates.
            x = (x + 1.0) * width / 2.0;
            y = (y + 1.0) * height / 2.0;

            // Discard stars that are outside boundaries (due to possible rounding errors).
            if (x < 0 || x >= width || y < 0 || y >= height)
                continue;

            // See if new star is too close to any existing star.
            double lowest_dist=CalcNewPosNearestNeighbour(std::pair<double,double>(x,y),positions);

            // If so, we try again.
            if (lowest_dist < MIN_SYSTEM_SEPARATION * MIN_SYSTEM_SEPARATION && attempts < MAX_ATTEMPTS_PLACE_SYSTEM - 1) {
                --i;
                continue;
            }

            // Add the new star location.
            positions.push_back(std::make_pair(x, y));

            // Note that attempts is reset for every star.
            attempts = 0;
        }
#else
        throw std::runtime_error("Non-server called EllipticalGalaxyCalcPositions; only server should call this while creating the universe");
#endif
    }

    void ClusterGalaxyCalcPositions(std::vector<std::pair<double,double> > &positions, unsigned int clusters, unsigned int stars, double width, double height)
    {
#ifdef FREEORION_BUILD_SERVER
        assert(clusters);
        assert(stars);

        // probability of systems which don't belong to a cluster
        const double system_noise = 0.15;
        double ellipse_width_vs_height = RandDouble(0.2,0.5);
        // first innermost pair hold cluster position, second innermost pair stores help values for cluster rotation (sin,cos)
        std::vector<std::pair<std::pair<double,double>,std::pair<double,double> > > clusters_position;
        unsigned int i,j,attempts;

        DoubleDistType    random_zero_to_one = DoubleDist  (0.0,  1.0);
        DoubleDistType    random_angle  = DoubleDist  (0.0,2.0*PI);

        for (i=0,attempts=0;i<clusters && static_cast<int>(attempts)<MAX_ATTEMPTS_PLACE_SYSTEM;i++,attempts++)
        {
            // prevent cluster position near borders (and on border)
            double x=((random_zero_to_one()*2.0-1.0) /(clusters+1.0))*clusters,
                y=((random_zero_to_one()*2.0-1.0) /(clusters+1.0))*clusters;


            // ensure all clusters have a min separation to each other (search isn't opimized, not worth the effort)
            for (j=0;j<clusters_position.size();j++)
                if ((clusters_position[j].first.first - x)*(clusters_position[j].first.first - x)+ (clusters_position[j].first.second - y)*(clusters_position[j].first.second - y)
                    < (2.0/clusters))
                    break;
            if (j<clusters_position.size())
            {
                i--;
                continue;
            }

            attempts=0;
            double rotation = RandDouble(0.0,PI);
            clusters_position.push_back(std::pair<std::pair<double,double>,std::pair<double,double> >(std::pair<double,double>(x,y),std::pair<double,double>(sin(rotation),cos(rotation))));
        }

        for (i=0,attempts=0; i < stars && attempts<100; i++,attempts++ )
        {
            double x,y;
            if (random_zero_to_one()<system_noise)
            {
                x = random_zero_to_one() * 2.0 - 1.0;
                y = random_zero_to_one() * 2.0 - 1.0;
            }
            else
            {
                short  cluster = i%clusters_position.size();
                double radius  = random_zero_to_one();
                double angle   = random_angle();
                double x1,y1;

                x1 = radius * cos(angle);
                y1 = radius * sin(angle)*ellipse_width_vs_height;

                x = x1*clusters_position[cluster].second.second + y1*clusters_position[cluster].second.first;
                y =-x1*clusters_position[cluster].second.first  + y1*clusters_position[cluster].second.second;

                x = x/sqrt((double)clusters) + clusters_position[cluster].first.first;
                y = y/sqrt((double)clusters) + clusters_position[cluster].first.second;
            }
            x = (x+1)*width /2.0;
            y = (y+1)*height/2.0;

            if (x<0 || width<=x || y<0 || height<=y)
                continue;

            // See if new star is too close to any existing star.
            double lowest_dist=CalcNewPosNearestNeighbour(std::pair<double,double>(x,y),positions);

            // If so, we try again.
            if (lowest_dist < MIN_SYSTEM_SEPARATION * MIN_SYSTEM_SEPARATION && attempts < MAX_ATTEMPTS_PLACE_SYSTEM - 1) {
                --i;
                continue;
            }

            // Add the new star location.
            positions.push_back(std::make_pair(x, y));

            // Note that attempts is reset for every star.
            attempts = 0;
        }
#else
        throw std::runtime_error("Non-server called ClusterGalaxyCalcPositions; only server should call this while creating the universe");
#endif
    }

    void RingGalaxyCalcPositions(std::vector<std::pair<double, double> > &positions, unsigned int stars, double width, double height)
    {
#ifdef FREEORION_BUILD_SERVER
        double RING_WIDTH = width / 4.0;
        double RING_RADIUS = (width - RING_WIDTH) / 2.0;

        DoubleDistType   theta_dist = DoubleDist(0.0, 2.0 * PI);
        GaussianDistType radius_dist = GaussianDist(RING_RADIUS, RING_WIDTH / 3.0);

        for (unsigned int i = 0, attempts = 0; i < stars && static_cast<int>(attempts) < MAX_ATTEMPTS_PLACE_SYSTEM; ++i, ++attempts)
        {
            double theta = theta_dist();
            double radius = radius_dist();

            double x = width / 2.0 + radius * std::cos(theta);
            double y = height / 2.0 + radius * std::sin(theta);

            if (x < 0 || width <= x || y < 0 || height <= y)
                continue;

            // See if new star is too close to any existing star.
            double lowest_dist=CalcNewPosNearestNeighbour(std::pair<double,double>(x,y),positions);

            // If so, we try again.
            if (lowest_dist < MIN_SYSTEM_SEPARATION * MIN_SYSTEM_SEPARATION && attempts < MAX_ATTEMPTS_PLACE_SYSTEM - 1) {
                --i;
                continue;
            }

            // Add the new star location.
            positions.push_back(std::make_pair(x, y));

            // Note that attempts is reset for every star.
            attempts = 0;
        }
#else
        throw std::runtime_error("Non-server called RingGalaxyCalcPositions; only server should call this while creating the universe");
#endif
    }

    System* GenerateSystem(Universe &universe, Age age, double x, double y)
    {
#ifdef FREEORION_BUILD_SERVER
        const std::vector<int>& base_star_type_dist = UniverseDataTables()["BaseStarTypeDist"][0];
        const std::vector<std::vector<int> >& universe_age_mod_to_star_type_dist = UniverseDataTables()["UniverseAgeModToStarTypeDist"];

        static std::list<std::string> star_names;
        if (star_names.empty())
            LoadSystemNames(star_names);

        // generate new star
        int star_name_idx = RandSmallInt(0, static_cast<int>(star_names.size()) - 1);
        std::list<std::string>::iterator it = star_names.begin();
        std::advance(it, star_name_idx);
        std::string star_name(*it);
        star_names.erase(it);

        // make a series of "rolls" (1-100) for each planet size, and take the highest modified roll
        int idx = 0;
        int max_roll = 0;
        for (unsigned int i = 0; i < NUM_STAR_TYPES; ++i) {
            int roll = g_hundred_dist() + universe_age_mod_to_star_type_dist[age][i] + base_star_type_dist[i];
            if (max_roll < roll) {
                max_roll = roll;
                idx = i;
            }
        }
        System* system = new System(StarType(idx), MAX_SYSTEM_ORBITS, star_name, x, y);

        int new_system_id = universe.Insert(system);
        if (new_system_id == UniverseObject::INVALID_OBJECT_ID) {
            throw std::runtime_error("Universe::GenerateIrregularGalaxy() : Attempt to insert system " +
                                     star_name + " into the object map failed.");
        }
        return system;
#else
        throw std::runtime_error("Non-server called GenerateSystem; only server should call this while creating the universe");
#endif
    }

    void GenerateStarField(Universe &universe, Age age, const std::vector<std::pair<double, double> > &positions, 
                           Universe::AdjacencyGrid& adjacency_grid, double adjacency_box_size)
    {
#ifdef FREEORION_BUILD_SERVER
        // generate star field
        for (unsigned int star_cnt = 0; star_cnt < positions.size(); ++star_cnt) {
            System* system = GenerateSystem(universe, age, positions[star_cnt].first, positions[star_cnt].second);
            adjacency_grid[static_cast<int>(system->X() / adjacency_box_size)]
                [static_cast<int>(system->Y() / adjacency_box_size)].insert(system);
        }
#else
        throw std::runtime_error("Non-server called GenerateStarField; only server should call this while creating the universe");
#endif
    }

    void GetNeighbors(double x, double y, const Universe::AdjacencyGrid& adjacency_grid, std::set<System*>& neighbors)
    {
#ifdef FREEORION_BUILD_SERVER
        const double ADJACENCY_BOX_SIZE = Universe::UniverseWidth() / ADJACENCY_BOXES;
        std::pair<unsigned int, unsigned int> grid_box(static_cast<unsigned int>(x / ADJACENCY_BOX_SIZE),
                                                       static_cast<unsigned int>(y / ADJACENCY_BOX_SIZE));

        // look in the box into which this system falls, and those boxes immediately around that box
        neighbors = adjacency_grid[grid_box.first][grid_box.second];

        if (0 < grid_box.first) {
            if (0 < grid_box.second) {
                const std::set<System*>& grid_square = adjacency_grid[grid_box.first - 1][grid_box.second - 1];
                neighbors.insert(grid_square.begin(), grid_square.end());
            }
            const std::set<System*>& grid_square = adjacency_grid[grid_box.first - 1][grid_box.second];
            neighbors.insert(grid_square.begin(), grid_square.end());
            if (grid_box.second < adjacency_grid[grid_box.first].size() - 1) {
                const std::set<System*>& grid_square = adjacency_grid[grid_box.first - 1][grid_box.second + 1];
                neighbors.insert(grid_square.begin(), grid_square.end());
            }
        }
        if (0 < grid_box.second) {
            const std::set<System*>& grid_square = adjacency_grid[grid_box.first][grid_box.second - 1];
            neighbors.insert(grid_square.begin(), grid_square.end());
        }
        if (grid_box.second < adjacency_grid[grid_box.first].size() - 1) {
            const std::set<System*>& grid_square = adjacency_grid[grid_box.first][grid_box.second + 1];
            neighbors.insert(grid_square.begin(), grid_square.end());
        }

        if (grid_box.first < adjacency_grid.size() - 1) {
            if (0 < grid_box.second) {
                const std::set<System*>& grid_square = adjacency_grid[grid_box.first + 1][grid_box.second - 1];
                neighbors.insert(grid_square.begin(), grid_square.end());
            }
            const std::set<System*>& grid_square = adjacency_grid[grid_box.first + 1][grid_box.second];
            neighbors.insert(grid_square.begin(), grid_square.end());
            if (grid_box.second < adjacency_grid[grid_box.first].size() - 1) {
                const std::set<System*>& grid_square = adjacency_grid[grid_box.first + 1][grid_box.second + 1];
                neighbors.insert(grid_square.begin(), grid_square.end());
            }
        }
#else
        throw std::runtime_error("Non-server called GetNeighbors; only server should call this while creating the universe");
#endif
    }
}

#ifdef FREEORION_BUILD_SERVER
namespace Delauney {
    // simple 2D point.  would have used array of systems, but System class has limits on the range of 
    // position values that would interfere with the triangulation algorithm (need a single large covering
    // triangle that overlaps all actual points being triangulated)
    class DTPoint {
    public:
        double x;
        double y;

        DTPoint(double xp, double yp);
        DTPoint();
    };
    DTPoint::DTPoint() {
        x = 0;
        y = 0;
    };
    DTPoint::DTPoint(double xp, double yp) {
        x = xp;
        y = yp;
    };

    // simple class for an integer that has an associated "sorting value", so the integer can be stored in
    // a list sorted by something other than the value of the integer
    class SortValInt {
    public:
        int num;
        double sortVal;
        
        SortValInt(int n, double s);
    };
    SortValInt::SortValInt(int n, double s) {
        num = n;
        sortVal = s;
    };
    
    // list of three interger array indices, and some additional info about the triangle that the corresponding
    // points make up, such as the circumcentre and radius, and a function to find if another point is in the
    // circumcircle
    class DTTriangle {
    private:
        std::vector<int> verts;  // indices of vertices of triangle
        Delauney::DTPoint centre;  // location of circumcentre of triangle
        double radius2;  // radius of circumcircle squared

    public:
        // determines whether a specified point is within the circumcircle of the triangle
        bool PointInCircumCircle(Delauney::DTPoint &p);
        
        const std::vector<int>& getVerts(); // getter

        DTTriangle(int vert1, int vert2, int vert3, std::vector<Delauney::DTPoint> &points);
        DTTriangle();
    };

    // determines whether a specified point is within the circumcircle of the triangle
    bool DTTriangle::PointInCircumCircle(Delauney::DTPoint &p) {
        double vectX, vectY;

        vectX = p.x - centre.x;
        vectY = p.y - centre.y;

        if (vectX*vectX + vectY*vectY < radius2)
            return true;
        return false;
    };

    DTTriangle::DTTriangle(int vert1, int vert2, int vert3, std::vector<Delauney::DTPoint> &points) {
        double a, Sx, Sy, b;
        double x1, x2, x3, y1, y2, y3;

        if ( vert1 == vert2 || vert1 == vert3 || vert2 == vert3)
            throw std::runtime_error("Attempted to create Triangle with two of the same vertex indices.");

        verts = std::vector<int>(3);

        // record indices of vertices of triangle
        verts[0] = vert1;
        verts[1] = vert2;
        verts[2] = vert3;

        // extract position info for vertices
        x1 = points[vert1].x;
        x2 = points[vert2].x;
        x3 = points[vert3].x;
        y1 = points[vert1].y;
        y2 = points[vert2].y;
        y3 = points[vert3].y;
            
        // calculate circumcircle and circumcentre of triangle
        a = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2);
            
        Sx = 0.5 * ((x1 * x1 + y1 * y1) * (y2 - y3) +
                     (x2 * x2 + y2 * y2) * (y3 - y1) +
                     (x3 * x3 + y3 * y3) * (y1 - y2));

        Sy = -0.5* ((x1 * x1 + y1 * y1) * (x2 - x3) +
                    (x2 * x2 + y2 * y2) * (x3 - x1) +
                    (x3 * x3 + y3 * y3) * (x1 - x2));

        b =   (    (x1 * x1 + y1 * y1) * (x2 * y3 - x3 * y2) +
                (x2 * x2 + y2 * y2) * (x3 * y1 - x1 * y3) +
                (x3 * x3 + y3 * y3) * (x1 * y2 - x2 * y1));
            
        // make sure nothing funky's going on...
        if (std::abs(a) < 0.01)
            throw std::runtime_error("Attempted to find circumcircle for a triangle with vertices in a line.");
                    
        // finish!
        centre.x = Sx / a;
        centre.y = Sy / a;
        radius2 = (Sx*Sx + Sy*Sy)/(a*a) + b/a;
    };


    DTTriangle::DTTriangle() {
        verts = std::vector<int>(3, 0);
        centre.x = 0;
        centre.y = 0;
        radius2 = 0;
    };

    const std::vector<int>& DTTriangle::getVerts() {
        return verts;
    };


    // runs a Delauney Triangulation routine on a set of 2D points extracted from an array of systems
    // returns the list of triangles produced
    std::list<Delauney::DTTriangle>* DelauneyTriangulate(std::vector<System*> &systems);
    
    // does Delauney Triangulation to generate starlanes
    std::list<Delauney::DTTriangle>* DelauneyTriangulate(std::vector<System*> &systems) {

        int n, c, theSize, num, num2; // loop counters, storage for retreived size of a vector, temp storage
        std::list<Delauney::DTTriangle>::iterator itCur, itEnd;
        std::list<Delauney::SortValInt>::iterator itCur2, itEnd2; 
        // vector of x and y positions of stars
        std::vector<Delauney::DTPoint> points;    
        // pointer to main list of triangles algorithm works with.
        std::list<Delauney::DTTriangle> *triList;
        // list of indices in vector of points extracted from removed triangles that need to be retriangulated
        std::list<Delauney::SortValInt> pointNumList;
        double vx, vy, mag;  // vector components, magnitude
    
        // ensure a useful list of systems was passed...
        if (systems.empty())
            throw std::runtime_error("Attempted to run Delauney Triangulation on empty array of systems");
    
        // extract systems positions, and store in vector.  Can't use actual systems data since
        // systems have position limitations which would interfere with algorithm    
        theSize = static_cast<int>(systems.size());
        for (n = 0; n < theSize; n++) {        
            points.push_back(Delauney::DTPoint(systems[n]->X(), systems[n]->Y()));    
        }
    
        // add points for covering triangle.  the point positions should be big enough to form a triangle
        // that encloses all the systems of the galaxy (or at least one whose circumcircle covers all points)
        points.push_back(Delauney::DTPoint(-1.0, -1.0));
        points.push_back(Delauney::DTPoint(2.0 * (Universe::UniverseWidth() + 1.0), -1.0));
        points.push_back(Delauney::DTPoint(-1.0, 2.0 * (Universe::UniverseWidth() + 1.0)));

        // initialize triList.  algorithm adds and removes triangles from this list, and the resulting 
        // list is returned (so should be deleted externally)
        triList = new std::list<Delauney::DTTriangle>;
        
        // add last three points into the first triangle, the "covering triangle"
        theSize = static_cast<int>(points.size());
        triList->push_front(Delauney::DTTriangle(theSize-1, theSize-2, theSize-3, points));
    
        
        // loop through "real" points (from systems, not the last three added to make the covering triangle)
        for (n = 0; n < theSize - 3; n++) {
            pointNumList.clear();

            // check each triangle in list, to see if the new point lies in its circumcircle.  if so, delete
            // the triangle and add its vertices to a list 
            itCur = triList->begin();
            itEnd = triList->end();        
            while (itCur != itEnd) {
                // get current triangle
                Delauney::DTTriangle& tri = *itCur;

                // check if point to be added to triangulation is within the circumcircle for the current triangle
                if (tri.PointInCircumCircle(points[n])) {
                    // if so, insert the triangles vertices indices into the list.  add in sorted position
                    // based on angle of direction to current point n being inserted.  don't add if doing
                    // so would duplicate an index already in the list
                    for (c = 0; c < 3; c++) {
                        num = (tri.getVerts())[c];  // store "current point"
                        
                        // get sorting value to order points clockwise circumferentially around point n
                        // vector from point n to current point
                        vx = points[num].x - points[n].x;
                        vy = points[num].y - points[n].y;
                        mag = sqrt(vx*vx + vy*vy);
                        // normalize
                        vx /= mag;
                        vy /= mag;
                        // dot product with (0, 1) is vy, magnitude of cross product is vx
                        // this gives a range of "sortValue" from -2 to 2, around the circle
                        if (vx >= 0) mag = vy + 1; else mag = -vy - 1;
                        // sorting value in "mag"

                        // iterate through list, finding insert spot and verifying uniqueness (or add if list is empty)
                        itCur2 = pointNumList.begin();
                        itEnd2 = pointNumList.end();
                        if (itCur2 == itEnd2) {
                            // list is empty
                            pointNumList.push_back(Delauney::SortValInt(num, mag));
                        }
                        else {
                            while (itCur2 != itEnd2) {
                                if ((*itCur2).num == num) 
                                    break;
                                if ((*itCur2).sortVal > mag) {
                                    pointNumList.insert(itCur2, Delauney::SortValInt(num, mag));
                                    break;
                                }                            
                                itCur2++;
                            }
                            if (itCur2 == itEnd2) {
                                // point wasn't added, so should go at end
                                pointNumList.push_back(Delauney::SortValInt(num, mag));
                            }
                        }
                    } // end for c

                    // remove current triangle from list of triangles
                    itCur = triList->erase(itCur);
                }
                else {
                    // point not in circumcircle for this triangle
                    // to go next triangle in list
                    ++itCur;
                }
            } // end while

            // go through list of points, making new triangles out of them
            itCur2 = pointNumList.begin();
            itEnd2 = pointNumList.end();
            assert(itCur2 != itEnd2);

            // add triangle for last and first points and n
            triList->push_front(Delauney::DTTriangle(n, (pointNumList.front()).num, (pointNumList.back()).num, points));
            
            num = (*itCur2).num;
            ++itCur2;
            while (itCur2 != itEnd2) {
                num2 = num;                
                num = (*itCur2).num;
                
                triList->push_front(Delauney::DTTriangle(n, num2, num, points));
                
                ++itCur2;
            } // end while
            
        } // end for        
        return triList;
    } // end function
} // end namespace
#endif
void Universe::CreateUniverse(int size, Shape shape, Age age, StarlaneFrequency starlane_freq, PlanetDensity planet_density, 
                              SpecialsFrequency specials_freq, int players, int ai_players, 
                              const std::map<int, PlayerSetupData>& player_setup_data)
{
#ifdef FREEORION_BUILD_SERVER
#ifdef FREEORION_RELEASE
    ClockSeed();
#endif

    // wipe out anything present in the object map
    for (ObjectMap::iterator itr = m_objects.begin(); itr != m_objects.end(); ++itr)
        delete itr->second;
    m_objects.clear();

    m_last_allocated_object_id = -1;
    m_last_allocated_design_id = -1;

    Logger().debugStream() << "Creating universe with " << size << " stars and " << players << " players.";

    std::vector<int> homeworlds;

    // a grid of ADJACENCY_BOXES x ADJACENCY_BOXES boxes to hold the positions of the systems as they are generated,
    // in order to ensure that they get spaced out properly
    AdjacencyGrid adjacency_grid(ADJACENCY_BOXES, std::vector<std::set<System*> >(ADJACENCY_BOXES));

    s_universe_width = std::sqrt(static_cast<double>(size)) * AVG_UNIVERSE_WIDTH;

    std::vector<std::pair<double, double> > positions;

    // generate the stars
    switch (shape) {
    case SPIRAL_2:
    case SPIRAL_3:
    case SPIRAL_4:
        SpiralGalaxyCalcPositions(positions, 2 + (shape - SPIRAL_2), size, s_universe_width, s_universe_width);
        GenerateStarField(*this, age, positions, adjacency_grid, s_universe_width / ADJACENCY_BOXES);
        break;
    case CLUSTER: {
        int average_clusters = size / 20; // chosen so that a "typical" size of 100 yields about 5 clusters
        if (!average_clusters)
            average_clusters = 2;
        int clusters = RandSmallInt(average_clusters * 8 / 10, average_clusters * 12 / 10); // +/- 20%
        ClusterGalaxyCalcPositions(positions, clusters, size, s_universe_width, s_universe_width);
        GenerateStarField(*this, age, positions, adjacency_grid, s_universe_width / ADJACENCY_BOXES);
        break;
    }
    case ELLIPTICAL:
        EllipticalGalaxyCalcPositions(positions, size, s_universe_width, s_universe_width);
        GenerateStarField(*this, age, positions, adjacency_grid, s_universe_width / ADJACENCY_BOXES);
        break;
    case IRREGULAR:
        GenerateIrregularGalaxy(size, age, adjacency_grid);
        break;
    case RING:
        RingGalaxyCalcPositions(positions, size, s_universe_width, s_universe_width);
        GenerateStarField(*this, age, positions, adjacency_grid, s_universe_width / ADJACENCY_BOXES);
        break;
    default:
        Logger().errorStream() << "Universe::Universe : Unknown galaxy shape: " << shape << ".  Using IRREGULAR as default.";
        GenerateIrregularGalaxy(size, age, adjacency_grid);
    }

    PopulateSystems(planet_density, specials_freq);
    GenerateStarlanes(starlane_freq, adjacency_grid);
    InitializeSystemGraph();
    GenerateHomeworlds(players + ai_players, homeworlds);
    NamePlanets();
    GenerateEmpires(players + ai_players, homeworlds, player_setup_data);

    // Apply non-effect meter adjustments
    for (Universe::const_iterator it = GetUniverse().begin(); it != GetUniverse().end(); ++it) {
        it->second->ResetMaxMeters();   // zero all meters
        it->second->ApplyUniverseTableMaxMeterAdjustments();  // apply non-effects max meter modifications, including focus mods
    }

    // Apply effects for 1st turn
    ApplyEffects();

    // update initial and previous meter values
    for (Universe::const_iterator it = GetUniverse().begin(); it != GetUniverse().end(); ++it) {
        it->second->ClampMeters();  // limit current meters by max meters
        for (MeterType i = MeterType(0); i != NUM_METER_TYPES; i = MeterType(i + 1)) {
            if (Meter* meter = it->second->GetMeter(i)) {
                meter->m_previous_current = meter->m_current;
                meter->m_previous_max = meter->m_max;
                meter->m_initial_current = meter->m_current;
                meter->m_initial_max = meter->m_max;
            }
        }
    }

#else
        throw std::runtime_error("Non-server called Universe::CreateUniverse; only server should call this while creating the universe");
#endif
}

void Universe::GenerateIrregularGalaxy(int stars, Age age, AdjacencyGrid& adjacency_grid)
{
#ifdef FREEORION_BUILD_SERVER
    SmallIntDistType star_type_gen = SmallIntDist(0, NUM_STAR_TYPES - 1);

    // generate star field
    for (int star_cnt = 0; star_cnt < stars; ++star_cnt) {
        // generate new star
        const double ADJACENCY_BOX_SIZE = UniverseWidth() / ADJACENCY_BOXES;

        bool placed = false;
        int attempts_left = 25;
        while (!placed && attempts_left--) {
            // make sure this system doesn't get slapped down too close to or on top of any systems
            std::set<System*> neighbors;
            double x = (s_universe_width - 0.1) * RandZeroToOne(),
                y = (s_universe_width - 0.1) * RandZeroToOne();
            GetNeighbors(x, y, adjacency_grid, neighbors);

            bool too_close = false;
            for (std::set<System*>::iterator it = neighbors.begin(); it != neighbors.end(); ++it) {
                double x_dist = x - (*it)->X();
                double y_dist = y - (*it)->Y();
                if (x_dist * x_dist + y_dist * y_dist < MIN_SYSTEM_SEPARATION * MIN_SYSTEM_SEPARATION) {
                    too_close = true;
                    break;
                }
            }

            if (!too_close) {
                System* system = GenerateSystem(*this, age, x, y);
                adjacency_grid[static_cast<int>(system->X() / ADJACENCY_BOX_SIZE)]
                    [static_cast<int>(system->Y() / ADJACENCY_BOX_SIZE)].insert(system);
                placed = true;
            }
        }
    }
#else
        throw std::runtime_error("Non-server called Universe::GenerateIrregularGalaxy; only server should call this while creating the universe");
#endif
}

void Universe::PopulateSystems(PlanetDensity density, SpecialsFrequency specials_freq)
{
#ifdef FREEORION_BUILD_SERVER
    std::vector<System*> sys_vec = FindObjects<System>();

    if (sys_vec.empty())
        throw std::runtime_error("Attempted to populate an empty galaxy.");

    const std::vector<std::vector<int> >& density_mod_to_planet_size_dist = UniverseDataTables()["DensityModToPlanetSizeDist"];
    const std::vector<std::vector<int> >& star_color_mod_to_planet_size_dist = UniverseDataTables()["StarColorModToPlanetSizeDist"];
    const std::vector<std::vector<int> >& slot_mod_to_planet_size_dist = UniverseDataTables()["SlotModToPlanetSizeDist"];
    const std::vector<std::vector<int> >& planet_size_mod_to_planet_type_dist = UniverseDataTables()["PlanetSizeModToPlanetTypeDist"];
    const std::vector<std::vector<int> >& slot_mod_to_planet_type_dist = UniverseDataTables()["SlotModToPlanetTypeDist"];
    const std::vector<std::vector<int> >& star_color_mod_to_planet_type_dist = UniverseDataTables()["StarColorModToPlanetTypeDist"];

    double planetary_special_chance = UniverseDataTables()["SpecialsFrequency"][0][specials_freq] / 10000.0;
    const std::set<std::string>& special_names = PlanetSpecialNames();
    SmallIntDistType specials_dist = SmallIntDist(0, special_names.size() - 1);

    for (std::vector<System*>::iterator it = sys_vec.begin(); it != sys_vec.end(); ++it) {
        System* system = *it;

        for (int orbit = 0; orbit < system->Orbits(); orbit++) {
            // make a series of "rolls" (1-100) for each planet size, and take the highest modified roll
            int idx = 0;
            int max_roll = 0;
            for (unsigned int i = 0; i < NUM_PLANET_SIZES; ++i) {
                int roll = g_hundred_dist() + star_color_mod_to_planet_size_dist[system->Star()][i] + slot_mod_to_planet_size_dist[orbit][i]
                    + density_mod_to_planet_size_dist[density][i];
                if (max_roll < roll) {
                    max_roll = roll;
                    idx = i;
                }
            }
            PlanetSize planet_size = PlanetSize(idx);

            if (planet_size == SZ_NOWORLD)
                continue;

            if (planet_size == SZ_ASTEROIDS) {
                idx = PT_ASTEROIDS;
            } else if (planet_size == SZ_GASGIANT) {
                idx = PT_GASGIANT;
            } else {
                // make another series of modified rolls for planet type
                for (unsigned int i = 0; i < NUM_PLANET_TYPES; ++i) {
                    int roll = g_hundred_dist() + planet_size_mod_to_planet_type_dist[planet_size][i] + slot_mod_to_planet_type_dist[orbit][i] + 
                        star_color_mod_to_planet_type_dist[system->Star()][i];
                    if (max_roll < roll) {
                        max_roll = roll;
                        idx = i;
                    }
                }
            }
            PlanetType planet_type = PlanetType(idx);

            if (planet_type == PT_ASTEROIDS)
                planet_size = SZ_ASTEROIDS;
            if (planet_type == PT_GASGIANT)
                planet_size = SZ_GASGIANT;

            Planet* planet = new Planet(planet_type, planet_size);

            if (planet_type != PT_ASTEROIDS && planet_type != PT_GASGIANT && !special_names.empty() && RandZeroToOne() < planetary_special_chance) {
                std::set<std::string>::const_iterator name_it = special_names.begin();
                std::advance(name_it, specials_dist());
                planet->AddSpecial(*name_it);
            }

            Insert(planet); // add planet to universe map
            system->Insert(planet, orbit);  // add planet to system map
        }
    }
#else
        throw std::runtime_error("Non-server called Universe::PopulateSystems; only server should call this while creating the universe");
#endif
}

void Universe::GenerateStarlanes(StarlaneFrequency freq, const AdjacencyGrid& adjacency_grid)
{
#ifdef FREEORION_BUILD_SERVER
    if (freq == LANES_NONE)
        return;

    int numSys, s1, s2, s3; // numbers of systems, indices in vec_sys
    int n; // loop counter

    std::vector<int> triVerts;  // indices of stars that form vertices of a triangle
    
    // array of set to store final, included starlanes for each star
    std::vector<std::set<int> > laneSetArray;
    
    // array of set to store possible starlanes for each star, as extracted form triangulation
    std::vector<std::set<int> > potentialLaneSetArray;

    // iterators for traversing lists of starlanes
    std::set<int>::iterator laneSetIter, laneSetEnd, laneSetIter2, laneSetEnd2;
    
    // get systems
    std::vector<System*> sys_vec = FindObjects<System>();

    // pass systems to Delauney Triangulation routine, getting array of triangles back
    std::list<Delauney::DTTriangle> *triList = Delauney::DelauneyTriangulate(sys_vec);
    if (NULL == triList) return;
    
    if (triList->empty())
        throw std::runtime_error("Got blank list of triangles from Triangulation.");

    Delauney::DTTriangle tri;

    // convert passed StarlaneFrequency freq into maximum number of starlane jumps between systems that are
    // "adjacent" in the delauney triangulation.  (separated by a single potential starlane).
    // these numbers can and should be tweaked or extended
    int maxJumpsBetweenSystems = UniverseDataTables()["MaxJumpsBetweenSystems"][0][freq];
    
    numSys = sys_vec.size();  // (actually = number of systems + 1)

    // initialize arrays...
    potentialLaneSetArray.resize(numSys);
    for (n = 0; n < numSys; n++) {
        potentialLaneSetArray[n].clear();
    }
    laneSetArray.resize(numSys);
    for (n = 0; n < numSys; n++) {
        laneSetArray[n].clear();
    }

    // extract triangles from list, add edges to sets of potential starlanes for each star (in array)
    while (!triList->empty()) {
        tri = triList->front();
                
        triVerts = tri.getVerts();
        s1 = triVerts[0];
        s2 = triVerts[1];
        s3 = triVerts[2];

        // add starlanes to list of potential starlanes for each star, making sure each pair involves 
        // only stars that actually exist.  triangle generation uses three extra points which don't
        // represent actual systems and which need to be weeded out here.
        if ((s1 >= 0) && (s2 >= 0) && (s3 >= 0)) {
            if ((s1 < numSys) && (s2 < numSys)) {
                potentialLaneSetArray[s1].insert(s2);
                potentialLaneSetArray[s2].insert(s1);
            }
            if ((s1 < numSys) && (s3 < numSys)) {
                potentialLaneSetArray[s1].insert(s3);
                potentialLaneSetArray[s3].insert(s1);
            }
            if ((s2 < numSys) && (s3 < numSys)) {
                potentialLaneSetArray[s2].insert(s3);
                potentialLaneSetArray[s3].insert(s2);
            }
        }

        triList->pop_front();
    }

    // cleanup
    delete triList;

    //Logger().debugStream() << "Extracted Potential Starlanes from Triangulation";
    
    double maxStarlaneLength = UniverseDataTables()["MaxStarlaneLength"][0][0];
    CullTooLongLanes(maxStarlaneLength, potentialLaneSetArray, sys_vec);

    CullAngularlyTooCloseLanes(0.98, potentialLaneSetArray, sys_vec);

    //Logger().debugStream() << "Culled Agularly Too Close Lanes";

    for (n = 0; n < numSys; n++)
        laneSetArray[n].clear();

    // array of indices of systems from which to start growing spanning tree(s).  This can later be replaced with
    // some sort of user input.  It can also be ommited entirely, so just the ConnectedWithin loop below is used.
    std::vector<int> roots(4);
    roots[0] = 0;  roots[1] = 1;  roots[2] = 2;  roots[3] = 3;
    GrowSpanningTrees(roots, potentialLaneSetArray, laneSetArray);
    //Logger().debugStream() << "Constructed initial spanning trees.";
    
    // add starlanes of spanning tree to stars
    for (n = 0; n < numSys; n++) {
        laneSetIter = laneSetArray[n].begin();
        laneSetEnd = laneSetArray[n].end();
        while (laneSetIter != laneSetEnd) {
            s1 = *laneSetIter;
            // add the starlane to the stars
            sys_vec[n]->AddStarlane(s1);
            sys_vec[s1]->AddStarlane(n);
            laneSetIter++;
        } // end while
    } // end for n


    // loop through stars, seeing if any are too far away from stars they could be connected to by a
    // potential starlane.  If so, add the potential starlane to the stars to directly connect them
    for (n = 0; n < numSys; n++) {
        laneSetIter = potentialLaneSetArray[n].begin();
        laneSetEnd = potentialLaneSetArray[n].end();

        while (laneSetIter != laneSetEnd) {
            s1 = *laneSetIter;

            if (!ConnectedWithin(n, s1, maxJumpsBetweenSystems, laneSetArray)) {
                
                // add the starlane to the sets of starlanes for each star
                laneSetArray[n].insert(s1);
                laneSetArray[s1].insert(n);
                // add the starlane to the stars
                sys_vec[n]->AddStarlane(s1);
                sys_vec[s1]->AddStarlane(n);
            }

            laneSetIter++;
        } // end while
    } // end for n
#else
        throw std::runtime_error("Non-server called Universe::GenerateStarlanes; only server should call this while creating the universe");
#endif
}

void Universe::CullAngularlyTooCloseLanes(double maxLaneUVectDotProd, std::vector<std::set<int> >& laneSetArray, std::vector<System*> &systems)
{
#ifdef FREEORION_BUILD_SERVER
    // start and end systems of a new lane being considered, and end points of lanes that already exist with that
    // start at the start or destination of the new lane
    int curSys, dest1, dest2;
    
    // geometry stuff... points componenets, vector componenets dot product & magnitudes of vectors
    double startX, startY, vectX1, vectX2, vectY1, vectY2, dotProd, mag1, mag2;
    // 2 component vector and vect + magnitude typedefs
    
    typedef std::pair<double, double> VectTypeQQ;
    typedef std::pair<VectTypeQQ, double> VectAndMagTypeQQ;
    typedef std::pair<int, VectAndMagTypeQQ> MapInsertableTypeQQ;
    
    std::map<int, VectAndMagTypeQQ> laneVectsMap;  // componenets of vectors of lanes of current system, indexed by destination system number
    std::map<int, VectAndMagTypeQQ>::iterator laneVectsMapIter;
    
    VectTypeQQ tempVect;
    VectAndMagTypeQQ tempVectAndMag;
        
    // iterators to go through sets of lanes in array
    std::set<int>::iterator laneSetIter1, laneSetIter2, laneSetEnd;
    
    std::set<std::pair<int, int> > lanesToRemoveSet;  // start and end stars of lanes to be removed in final step...
    std::set<std::pair<int, int> >::iterator lanesToRemoveIter, lanesToRemoveEnd;
    std::pair<int, int> lane1, lane2;

    int curNumLanes;

    int numSys = systems.size();
    // make sure data is consistent
    if (static_cast<int>(laneSetArray.size()) != numSys) {
        //Logger().debugStream() << "CullAngularlyTooCloseLanes got different size vectors of lane sets and systems.  Doing nothing.";
        return;
    }
    
    if (numSys < 3) return;  // nothing worth doing for less than three systems

    //Logger().debugStream() << "Culling Too Close Angularly Lanes";

    // loop through systems
    for (curSys = 0; curSys < numSys; curSys++) {
        // get position of current system (for use in calculated vectors)
        startX = systems[curSys]->X();
        startY = systems[curSys]->Y();

        // get number of starlanes current system has
        curNumLanes = laneSetArray[curSys].size();

        // can't have pairs of lanes with less than two lanes...
        if (curNumLanes > 1) {
        
            // remove any old lane Vector Data
            laneVectsMap.clear();
            
            // get unit vectors for all lanes of this system
            laneSetIter1 = laneSetArray[curSys].begin();
            laneSetEnd = laneSetArray[curSys].end();
            while (laneSetIter1 != laneSetEnd) {
                // get destination for this lane
                dest1 = *laneSetIter1;
                // get vector to this lane destination
                vectX1 = systems[dest1]->X() - startX;
                vectY1 = systems[dest1]->Y() - startY;
                // normalize
                mag1 = std::sqrt(vectX1 * vectX1 + vectY1 * vectY1);
                vectX1 /= mag1;
                vectY1 /= mag1;

                // store lane in map of lane vectors
                tempVect = VectTypeQQ(vectX1, vectY1);
                tempVectAndMag = VectAndMagTypeQQ(tempVect, mag1);
                laneVectsMap.insert( MapInsertableTypeQQ(dest1, tempVectAndMag) );

                laneSetIter1++;
            }

            // iterate through lanes of curSys
            laneSetIter1 = laneSetArray[curSys].begin();
            laneSetIter1++;  // start at second, since iterators are used in pairs, and starting both at the first wouldn't be a valid pair
            while (laneSetIter1 != laneSetEnd) {
                // get destination of current starlane
                dest1 = *laneSetIter1;

                if (curSys < dest1) 
                    lane1 = std::pair<int, int>(curSys, dest1);
                else
                    lane1 = std::pair<int, int>(dest1, curSys);

                // check if this lane has already been added to the set of lanes to remove
                if (0 == lanesToRemoveSet.count(lane1)) {

                    // extract data on starlane vector...
                    laneVectsMapIter = laneVectsMap.find(dest1);
                    assert(laneVectsMapIter != laneVectsMap.end());
                    tempVectAndMag = laneVectsMapIter->second;
                    tempVect = tempVectAndMag.first;
                    vectX1 = tempVect.first;
                    vectY1 = tempVect.second;
                    mag1 = tempVectAndMag.second;
                    
                    // iterate through other lanes of curSys, in order to get all possible pairs of lanes
                    laneSetIter2 = laneSetArray[curSys].begin();
                    while (laneSetIter2 != laneSetIter1) {
                        dest2 = *laneSetIter2;

                        if (curSys < dest2) 
                            lane2 = std::pair<int, int>(curSys, dest2);
                        else
                            lane2 = std::pair<int, int>(dest2, curSys);

                        // check if this lane has already been added to the set of lanes to remove
                        if (0 == lanesToRemoveSet.count(lane2)) {
                                
                            // extract data on starlane vector...
                            laneVectsMapIter = laneVectsMap.find(dest2);
                            assert(laneVectsMapIter != laneVectsMap.end());
                            tempVectAndMag = laneVectsMapIter->second;
                            tempVect = tempVectAndMag.first;
                            vectX2 = tempVect.first;
                            vectY2 = tempVect.second;
                            mag2 = tempVectAndMag.second;

                            // find dot product
                            dotProd = vectX1 * vectX2 + vectY1 * vectY2;

                            // if dotProd is big enough, then lanes are too close angularly
                            // thus one needs to be removed.
                            if (dotProd > maxLaneUVectDotProd) {

                                 // preferentially remove the longer lane
                                if (mag1 > mag2) {
                                    lanesToRemoveSet.insert(lane1);
                                    break;  // don't need to check any more lanes against lane1, since lane1 has been removed
                                }
                                else {
                                    lanesToRemoveSet.insert(lane2);
                                }
                            }
                        }

                        laneSetIter2++;
                    }
                }
                
                laneSetIter1++;
            }
        }
    }

    // iterate through set of lanes to remove, and remove them in turn...
    lanesToRemoveIter = lanesToRemoveSet.begin();
    lanesToRemoveEnd = lanesToRemoveSet.end();
    while (lanesToRemoveIter != lanesToRemoveEnd) {
        lane1 = *lanesToRemoveIter;
        
        laneSetArray[lane1.first].erase(lane1.second);
        laneSetArray[lane1.second].erase(lane1.first);

        // check that removing lane hasn't disconnected systems
        if (!ConnectedWithin(lane1.first, lane1.second, numSys, laneSetArray)) {
            // they aren't connected... reconnect them
            laneSetArray[lane1.first].insert(lane1.second);
            laneSetArray[lane1.second].insert(lane1.first);
        }

        lanesToRemoveIter++;
    }
#else
        throw std::runtime_error("Non-server called Universe::CullAngularlyTooCloseLanes; only server should call this while creating the universe");
#endif
}

void Universe::CullTooLongLanes(double maxLaneLength, std::vector<std::set<int> >& laneSetArray, std::vector<System*> &systems)
{
#ifdef FREEORION_BUILD_SERVER
    // start and end systems of a new lane being considered, and end points of lanes that already exist with that start
    // at the start or destination of the new lane
    int curSys, dest;
    
    // geometry stuff... points components, vector componenets
    double startX, startY, vectX, vectY;
    
    // iterators to go through sets of lanes in array
    std::set<int>::iterator laneSetIter, laneSetEnd;
    
    // map, indexed by lane length, of start and end stars of lanes to be removed
    std::multimap<double, std::pair<int, int>, std::greater<double> > lanesToRemoveMap;
    std::multimap<double, std::pair<int, int>, std::greater<double> >::iterator lanesToRemoveIter, lanesToRemoveEnd;
    std::pair<int, int> lane;
    typedef std::pair<double, std::pair<int, int> > MapInsertableTypeQQ;

    int numSys = systems.size();
    // make sure data is consistent
    if (static_cast<int>(laneSetArray.size()) != numSys) {
        return;
    }
    
    if (numSys < 2) return;  // nothing worth doing for less than two systems (no lanes!)

    // get squared max lane lenth, so as to eliminate the need to take square roots of lane lenths...
    double maxLaneLength2 = maxLaneLength*maxLaneLength;

    // loop through systems
    for (curSys = 0; curSys < numSys; curSys++) {
        // get position of current system (for use in calculating vector)
        startX = systems[curSys]->X();
        startY = systems[curSys]->Y();

        // iterate through all lanes in system, checking lengths and marking to be removed if necessary
        laneSetIter = laneSetArray[curSys].begin();
        laneSetEnd = laneSetArray[curSys].end();
        while (laneSetIter != laneSetEnd) {
            // get destination for this lane
            dest = *laneSetIter;
            // convert start and end into ordered pair to represent lane
            if (curSys < dest) 
                lane = std::pair<int, int>(curSys, dest);
            else
                lane = std::pair<int, int>(dest, curSys);

            // get vector to this lane destination
            vectX = systems[dest]->X() - startX;
            vectY = systems[dest]->Y() - startY;
            
            // compare magnitude of vector to max allowed
            double laneLength2 = vectX*vectX + vectY*vectY;
            if (laneLength2 > maxLaneLength2) {
                // lane is too long!  mark it to be removed
                lanesToRemoveMap.insert( MapInsertableTypeQQ(laneLength2, lane) );
            }            

            laneSetIter++;            
        }
    }

    // Iterate through set of lanes to remove, and remove them in turn.  Since lanes were inserted in the map indexed by
    // their length, iteration starting with begin starts with the longest lane first, then moves through the lanes as
    // they get shorter, ensuring that the longest lanes are removed first.
    lanesToRemoveIter = lanesToRemoveMap.begin();
    lanesToRemoveEnd = lanesToRemoveMap.end();
    while (lanesToRemoveIter != lanesToRemoveEnd) {
        lane = lanesToRemoveIter->second;

        // ensure the lane still exists
        if (laneSetArray[lane.first].count(lane.second) > 0 &&
            laneSetArray[lane.second].count(lane.first) > 0) {

            // remove lane
            laneSetArray[lane.first].erase(lane.second);
            laneSetArray[lane.second].erase(lane.first);

            // if removing lane has disconnected systems, reconnect them
            if (!ConnectedWithin(lane.first, lane.second, numSys, laneSetArray)) {
                laneSetArray[lane.first].insert(lane.second);
                laneSetArray[lane.second].insert(lane.first);
            }
        }    
        lanesToRemoveIter++;
    }
#else
        throw std::runtime_error("Non-server called Universe::CullTooLongLanes; only server should call this while creating the universe");
#endif
}

void Universe::GrowSpanningTrees(std::vector<int> roots, std::vector<std::set<int> >& potentialLaneSetArray, std::vector<std::set<int> >& laneSetArray)
{
#ifdef FREEORION_BUILD_SERVER
    // array to keep track of whether a given system (index #) has been connected to by growing tree algorithm
    std::vector<int> treeOfSystemArray; // which growing tree a particular system has been assigned to
    
    //  map index by tree number, containing a list for each tree, each of which contains the systems in a particular tree
    std::map<int, std::list<int> > treeSysListsMap;
    std::map<int, std::list<int> >::iterator treeSysListsMapIter, treeSysListsMapEnd;
    std::pair<int, std::list<int> > mapInsertable;
    std::list<int> treeSysList, *pTreeSysList, *pTreeToMergeSysList;
    std::list<int>::iterator sysListIter;
    std::set<int>::iterator lanesSetIter, lanesSetEnd;
    
    int n, q, d, curTree, destTree, curSys, destSys, mergeSys;

    int numSys = potentialLaneSetArray.size();
    int numTrees = roots.size();

    // number of new connections to make from each connected node that is processed.  
    // could be made a parameter, possibly a function of the starlane frequency

    // make sure data is consistent
    if (static_cast<int>(laneSetArray.size()) != numSys) {
        //Logger().debugStream() << "GrowSpanningTrees got different size vectors of potential lane set(s) and systems.  Doing nothing.";
        return;
    }
    if ((numTrees < 1) || (numTrees > numSys)) {
        //Logger().debugStream() << "GrowSpanningTrees was asked to grow too many or too few trees simultaneously.  Doing nothing.";
        return;
    }
    if (static_cast<int>(roots.size()) > numSys) {
        //Logger().debugStream() << "GrowSpanningTrees was asked to grow more separate trees than there are systems to grow from.  Doing nothing.";
        return;
    }

    laneSetArray.resize(numSys);
        
    // set up data structures...
    treeOfSystemArray.resize(numSys);
    for (n = 0; n < numSys; n++) 
        treeOfSystemArray[n] = -1;  // sentinel value for not connected to any tree
    
    treeSysListsMap.clear();
    for (n = 0; n < numTrees; n++) {
        // check that next root is within valid range...
        q = roots[n];
        if ((q >= numSys) || (q < 0)) {
            //Logger().debugStream() << "GrowSpanningTrees was asked to grow to grow a tree from a system that doesn't exist.";
            return;
        }
        
        // make new tree to put into map
        treeSysList.clear();        
        treeSysList.push_front(q);
        
        // put new list into into map (for tree n), indexed by tree number
        mapInsertable = std::pair<int, std::list<int> >(n, treeSysList);        
        treeSysListsMap.insert(mapInsertable);
        
        // record the tree to which root system of tree n, roots[n], belongs (tree n)        
        treeOfSystemArray[q] = n;
    }

    //Logger().debugStream() << "Growing Trees Algorithm Starting...";
    
    // loop through map (indexed by tree number) of lists of systems, until map (and all lists) are empty...
    treeSysListsMapIter = treeSysListsMap.begin();
    treeSysListsMapEnd = treeSysListsMap.end();
    while (treeSysListsMapIter != treeSysListsMapEnd) {
        // extract number and list of tree
        curTree = treeSysListsMapIter->first;
        pTreeSysList = &(treeSysListsMapIter->second);

        if (pTreeSysList->empty()) {
            // no systems left for tree to grow.  Remove it from map of growing trees.
            treeSysListsMap.erase(curTree);
            //Logger().debugStream() << "Tree " << curTree << " was empty, so was removed from map of trees.";

            // check if set is empty...
            if (treeSysListsMap.empty()) break;  // and stop loop if it is
            // (iterator invalidated by erasing, so set to first tree remaining in map)
            treeSysListsMapIter = treeSysListsMap.begin();
        }
        else {            
            //Logger().debugStream() << "Tree " << curTree << " contains " << pTreeSysList->size() << " systems.";
            // tree has systems left to grow.
            
            // extract and remove a random system from the list
            
            // iterate to the position of the random system
            sysListIter = pTreeSysList->begin();
            for (d = RandSmallInt(0, pTreeSysList->size() - 1); d > 0; --d) // RandSmallInt(int min, int max);
                sysListIter++;
            
            curSys = *sysListIter; // extract
            pTreeSysList->erase(sysListIter); // erase
            
            //Logger().debugStream() << "Processing system " << curSys << " from tree " << curTree;

            // iterate through list of potential lanes for current system
            lanesSetIter = potentialLaneSetArray[curSys].begin();
            lanesSetEnd = potentialLaneSetArray[curSys].end();
            while (lanesSetIter != lanesSetEnd) {
                // get destination system of potential lane
                destSys = *lanesSetIter;
                
                // get which, if any, tree the destination system belongs to currently
                destTree = treeOfSystemArray[destSys];

                //Logger().debugStream() << "Considering lane from system " << curSys << " to system " << destSys << " of tree " << destTree;

                // check if the destination system already belongs to the current tree.
                if (curTree != destTree) {
                    // destination system is either in no tree, or is in a tree other than the current tree

                    // add lane between current and destination systems
                    laneSetArray[curSys].insert(destSys);
                    laneSetArray[destSys].insert(curSys);
                    
                    // mark destination system as part of this tree
                    treeOfSystemArray[destSys] = curTree;

                    //Logger().debugStream() << "Added lane from " << curSys << " to " << destSys << ", and added " << destSys << " to list of systems to process in tree " << curTree;
                }
                //else 
                //    Logger().debugStream() << "Both systems were already part of the same tree, so no lane was added";
                
                // check what, if any, tree the destination system was before being added to the current tree
                if (-1 == destTree) {
                    // destination system was not yet part of any tree.
                    // add system to list of systems to consider for this tree in future
                    pTreeSysList->push_back(destSys);

                    //Logger().debugStream() << "System was not yet part of an tree, so was added to the list of systems to process for tree " << curTree;
                }
                else if (destTree != curTree) {
                    // tree was already part of another tree
                    // merge the two trees.

                    //Logger().debugStream() << "Merging tree " << destTree << " into current tree " << curTree;

                    pTreeToMergeSysList = &((treeSysListsMap.find(destTree))->second);

                    //Logger().debugStream() << "...got pointer to systems list for tree to merge into current tree";
                    //Logger().debugStream() << "...list to merge has " << pTreeToMergeSysList->size() << " systems.";

                    // extract systems from tree to be merged into current tree
                    while (!pTreeToMergeSysList->empty()) {
                        // get system from list
                        mergeSys = pTreeToMergeSysList->front();
                        pTreeToMergeSysList->pop_front();
                        // add to current list
                        pTreeSysList->push_back(mergeSys);                        

                        //Logger().debugStream() << "Adding system " << mergeSys << " to current tree " << curTree << " from old tree " << destTree;
                    }

                    // reassign all systems from destination tree to current tree (gets systems even after they're removed
                    // from the list of systems for the dest tree)
                    for (q = 0; q < numSys; q++) 
                        if (treeOfSystemArray[q] == destTree)
                            treeOfSystemArray[q] = curTree;

                    treeSysListsMap.erase(destTree);
                }            
            
                lanesSetIter++;
            }
        }

        //Logger().debugStream() << "Moving to next tree...";
        
        treeSysListsMapIter++;
        treeSysListsMapEnd = treeSysListsMap.end();  // incase deleting or merging trees messed things up
        if (treeSysListsMapIter == treeSysListsMapEnd)
            treeSysListsMapIter = treeSysListsMap.begin();
    }
#else
        throw std::runtime_error("Non-server called Universe::GrowSpanningTrees; only server should call this while creating the universe");
#endif
}

void Universe::GenerateHomeworlds(int players, std::vector<int>& homeworlds)
{
#ifdef FREEORION_BUILD_SERVER
    homeworlds.clear();

    std::vector<System*> sys_vec = FindObjects<System>();

    if (sys_vec.empty())
        throw std::runtime_error("Attempted to generate homeworlds in an empty galaxy.");

    for (int i = 0; i < players; ++i) {
        int system_index;
        System* system;

        // make sure it has planets and it's not too close to the other homeworlds
        bool too_close = true;
        int attempts = 0;
        do {
            too_close = false;
            system_index = RandSmallInt(0, static_cast<int>(sys_vec.size()) - 1);
            system = sys_vec[system_index];
            for (unsigned int j = 0; j < homeworlds.size(); ++j) {
                System* existing_system = Object(homeworlds[j])->GetSystem();
                double x_dist = existing_system->X() - system->X();
                double y_dist = existing_system->Y() - system->Y();
                if (x_dist * x_dist + y_dist * y_dist < MIN_HOME_SYSTEM_SEPARATION * MIN_HOME_SYSTEM_SEPARATION) {
                    too_close = true;
                    break;
                }
            }
        } while ((!system->Orbits() || system->FindObjectIDs<Planet>().empty() || too_close) && ++attempts < 50);

        sys_vec.erase(sys_vec.begin() + system_index);

        // find a place to put the homeworld, and replace whatever planet is there already
        int planet_id, home_orbit; std::string planet_name;

        // we can only select a planet if there are planets in this system.
        if (system->Orbits()>0 && !system->FindObjects<Planet>().empty()) {
            std::vector<int> vec_orbits;
            for(int i=0;i<system->Orbits();i++)
                if(system->FindObjectIDsInOrbit<Planet>(i).size()>0)
                    vec_orbits.push_back(i);

            int planet_index = vec_orbits.size()>1?RandSmallInt(0, vec_orbits.size() - 1):0;
            planet_name = system->Name() + " " + RomanNumber(planet_index + 1);
            home_orbit = vec_orbits[planet_index];
            Delete(system->FindObjectIDsInOrbit<Planet>(home_orbit).back());
        } else {
            home_orbit = 0;
            planet_name = system->Name() + " " + RomanNumber(home_orbit + 1);
        }

        Planet* planet = new Planet(PT_TERRAN, SZ_MEDIUM);
        planet_id = Insert(planet);
        planet->Rename(planet_name);
        system->Insert(planet, home_orbit);

        homeworlds.push_back(planet_id);
    }
#else
        throw std::runtime_error("Non-server called Universe::GenerateHomeworlds; only server should call this while creating the universe");
#endif
}

void Universe::NamePlanets()
{
#ifdef FREEORION_BUILD_SERVER
    std::vector<System*> sys_vec = FindObjects<System>();
    for (std::vector<System*>::iterator it = sys_vec.begin(); it != sys_vec.end(); ++it) {
        System* system = *it;
        int num_planets_in_system = 0;
        for (int i = 0; i < system->Orbits(); i++) {
            std::vector<Planet*> planets = system->FindObjectsInOrbit<Planet>(i);
            if (!planets.empty()) {
                assert(planets.size() == 1);
                Planet* planet = planets[0];
                if (planet->Type() == PT_ASTEROIDS)
                    planet->Rename(UserString("PL_ASTEROID_BELT"));
                else
                    planet->Rename(system->Name() + " " + RomanNumber(++num_planets_in_system));
            }
        }
    }
#else
        throw std::runtime_error("Non-server called Universe::NamePlanets; only server should call this while creating the universe");
#endif
}

void Universe::GenerateEmpires(int players, std::vector<int>& homeworlds, const std::map<int, PlayerSetupData>& player_setup_data)
{
#ifdef FREEORION_BUILD_SERVER
    // create empires and assign homeworlds, names, colors, and fleet ranges to each one

    std::size_t i = 0;
    std::vector<GG::Clr> colors = EmpireColors();
    for (ServerNetworking::const_established_iterator it = ServerApp::GetApp()->Networking().established_begin(); it != ServerApp::GetApp()->Networking().established_end(); ++it, ++i) {
        std::string empire_name = UserString("EMPIRE") + boost::lexical_cast<std::string>(i);

        GG::Clr color;
        std::map<int, PlayerSetupData>::const_iterator setup_data_it = player_setup_data.find((*it)->ID());
        if (setup_data_it != player_setup_data.end()) { // first try to use user-assigned colors
            empire_name = setup_data_it->second.m_empire_name;
            color = setup_data_it->second.m_empire_color;
            std::vector<GG::Clr>::iterator color_it = std::find(colors.begin(), colors.end(), color);
            if (color_it != colors.end())
                colors.erase(color_it);
        } else if (!colors.empty()) { // failing that, use other built-in colors
            int color_idx = RandInt(0, colors.size() - 1);
            color = colors[color_idx];
            colors.erase(colors.begin() + color_idx);
        } else { // as a last resort, make up a color
            color = GG::FloatClr(RandZeroToOne(), RandZeroToOne(), RandZeroToOne(), 1.0);
        }

        int home_planet_id = homeworlds[i];

        // create new Empire object through empire manager
        Empire* empire = Empires().CreateEmpire((*it)->ID(), empire_name, (*it)->PlayerName(), color, home_planet_id);

        // set ownership of home planet
        int empire_id = empire->EmpireID();
        Planet* home_planet = Object<Planet>(homeworlds[i]);
        Logger().debugStream() << "Setting " << home_planet->GetSystem()->Name() << " (Planet #" <<  home_planet->ID()
                               << ") to be home system for Empire " << empire_id;
        home_planet->AddOwner(empire_id);

        System* home_system = home_planet->GetSystem();
        home_system->AddOwner(empire_id);

        // create population and industry on home planet
        home_planet->AddSpecial("HOMEWORLD_SPECIAL");
        home_planet->SetPrimaryFocus(FOCUS_BALANCED);
        home_planet->SetSecondaryFocus(FOCUS_BALANCED);
        home_planet->ResetMaxMeters();
        home_planet->ApplyUniverseTableMaxMeterAdjustments();
        Effect::EffectsGroup::TargetSet target_set;
        target_set.insert(home_planet);
        Special* special = GetSpecial("HOMEWORLD_SPECIAL");
        assert(special);
        for (unsigned int j = 0; j < special->Effects().size(); ++j) {
            special->Effects()[j]->Execute(home_planet->ID(), target_set);
        }
        home_planet->AdjustPop(home_planet->GetMeter(METER_HEALTH)->Max());
        home_planet->GetMeter(METER_HEALTH)->SetCurrent(home_planet->GetMeter(METER_HEALTH)->Max());
        home_planet->GetMeter(METER_CONSTRUCTION)->SetCurrent(home_planet->GetMeter(METER_CONSTRUCTION)->Max());
        home_planet->GetMeter(METER_FARMING)->SetCurrent(home_planet->GetMeter(METER_FARMING)->Max());
        home_planet->GetMeter(METER_INDUSTRY)->SetCurrent(home_planet->GetMeter(METER_INDUSTRY)->Max());
        home_planet->GetMeter(METER_MINING)->SetCurrent(home_planet->GetMeter(METER_MINING)->Max());
        home_planet->GetMeter(METER_RESEARCH)->SetCurrent(home_planet->GetMeter(METER_RESEARCH)->Max());
        home_planet->GetMeter(METER_TRADE)->SetCurrent(home_planet->GetMeter(METER_TRADE)->Max());
        home_planet->AdjustDefBases(3);

        home_planet->GetMeter(METER_HEALTH)->m_initial_current = home_planet->GetMeter(METER_HEALTH)->Current();
        home_planet->GetMeter(METER_HEALTH)->m_initial_max = home_planet->GetMeter(METER_HEALTH)->Max();
        home_planet->GetMeter(METER_CONSTRUCTION)->m_initial_current = home_planet->GetMeter(METER_CONSTRUCTION)->Current();
        home_planet->GetMeter(METER_CONSTRUCTION)->m_initial_max = home_planet->GetMeter(METER_CONSTRUCTION)->Max();
        home_planet->GetMeter(METER_FARMING)->m_initial_current = home_planet->GetMeter(METER_FARMING)->Current();
        home_planet->GetMeter(METER_FARMING)->m_initial_max = home_planet->GetMeter(METER_FARMING)->Max();
        home_planet->GetMeter(METER_INDUSTRY)->m_initial_current = home_planet->GetMeter(METER_INDUSTRY)->Current();
        home_planet->GetMeter(METER_INDUSTRY)->m_initial_max = home_planet->GetMeter(METER_INDUSTRY)->Max();
        home_planet->GetMeter(METER_MINING)->m_initial_current = home_planet->GetMeter(METER_MINING)->Current();
        home_planet->GetMeter(METER_MINING)->m_initial_max = home_planet->GetMeter(METER_MINING)->Max();
        home_planet->GetMeter(METER_RESEARCH)->m_initial_current = home_planet->GetMeter(METER_RESEARCH)->Current();
        home_planet->GetMeter(METER_RESEARCH)->m_initial_max = home_planet->GetMeter(METER_RESEARCH)->Max();
        home_planet->GetMeter(METER_TRADE)->m_initial_current = home_planet->GetMeter(METER_TRADE)->Current();
        home_planet->GetMeter(METER_TRADE)->m_initial_max = home_planet->GetMeter(METER_TRADE)->Max();


        // grant empire access to some initial buildings, ship parts and hulls
        empire->AddBuildingType("BLD_IMERIAL_PALACE");

        empire->AddPartType("SR_LASER");
        empire->AddPartType("SH_DEFENSE_GRID");
        empire->AddPartType("CO_COLONY_POD");

        empire->AddHullType("SH_SMALL");


        // create the empire's initial ship designs
        std::vector<std::string> parts;
        ShipDesign* design = new ShipDesign("Scout", "Small and cheap unarmed vessel designed for recon and exploration.",
                                            empire_id, 0, "SH_SMALL", parts, "misc/scout1.png", "model");
        int scout_design_id = empire->AddShipDesign(design);

        parts.push_back("CO_COLONY_POD");
        design = new ShipDesign("Colony Ship", "Huge unarmed vessel capable of delivering millions of citizens safely to new colony sites.",
                                empire_id, 0, "SH_MEDIUM", parts, "misc/colony1.png", "model");
        int colony_ship_design_id = empire->AddShipDesign(design);

        parts.clear();
        parts.push_back("SR_LASER");
        parts.push_back("SH_DEFENSE_GRID");
        design = new ShipDesign("Mark I", "Affordable armed patrol frigate.",
                                empire_id, 0, "SH_SMALL", parts, "misc/mark1.png", "model");
        int mark_I_design_id = empire->AddShipDesign(design);

        parts.clear();
        parts.push_back("SR_ION_CANNON");
        parts.push_back("SH_DEFENSE_GRID");
        design = new ShipDesign("Mark II", "Cruiser with strong defensive and offensive capabilities.",
                                empire_id, 0, "SH_SMALL", parts, "misc/mark2.png", "model");
        int temp = empire->AddShipDesign(design);

        parts.push_back("SR_ION_CANNON");
        parts.push_back("SH_DEFLECTOR");
        design = new ShipDesign("Mark III", "Advanced cruiser with heavy weaponry and armor to do the dirty work.",
                                empire_id, 0, "SH_MEDIUM", parts, "misc/mark3.png", "model");
        temp = empire->AddShipDesign(design);

        parts.push_back("SR_ION_CANNON");
        parts.push_back("SH_DEFLECTOR");
        design = new ShipDesign("Mark IV", "Massive state-of-art warship armed and protected with the latest technolgy. Priced accordingly.",
                                empire_id, 0, "SH_LARGE", parts, "misc/mark4.png", "model");
        temp = empire->AddShipDesign(design);


        // create the empire's starting fleet
        Fleet* home_fleet = new Fleet(UserString("FW_HOME_FLEET"), home_system->X(), home_system->Y(), empire_id);
        Insert(home_fleet);
        home_system->Insert(home_fleet);

        Ship* ship = 0;
        int ship_id = -1;

        // 5 scouts for The Silent One ot explore with
        for (int n = 0; n < 5; ++n) {
            ship = new Ship(empire_id, scout_design_id);
            ship->Rename(empire->NewShipName());
            ship_id = Insert(ship);
            home_fleet->AddShip(ship_id);
        }

        // 10 colony ships for The Silent One to test colonization
        for (int n = 0; n < 10; ++n) {
            ship = new Ship(empire_id, colony_ship_design_id);
            ship->Rename(empire->NewShipName());
            ship_id = Insert(ship);
            home_fleet->AddShip(ship_id);
        }

        // create a battle fleet
        Fleet* battle_fleet = new Fleet(UserString("FW_BATTLE_FLEET"), home_system->X(), home_system->Y(), empire_id);
        Insert(battle_fleet);
        home_system->Insert(battle_fleet);

        ship = new Ship(empire_id, mark_I_design_id);
        ship->Rename(empire->NewShipName());
        ship_id = Insert(ship);
        battle_fleet->AddShip(ship_id);
    }
#else
        throw std::runtime_error("Non-server called Universe::GenerateEmpires; only server should call this while creating the universe");
#endif
}

