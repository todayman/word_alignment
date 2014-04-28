#include <algorithm>
#include <fstream>
#include <iostream>
#include <numeric>
#include <sstream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using std::make_pair;
using std::make_tuple;

// Not everything needs to be a class
// If you're not using the self variable, that's a hint
std::vector<std::string> readFile(const std::string& fileName, unsigned numLines)
{
    std::vector<std::string> data;
    std::ifstream input(fileName);

    for( unsigned i = 0; i < numLines && input; ++i )
    {
        std::string str;
        std::getline(input, str);
        data.push_back(str);
    }

    return data;
}

void writeData(const std::string& filename, const std::vector<std::string>& lines)
{
    std::ofstream output(filename);
    for( const std::string& l : lines )
    {
        output << l << "\n";
    }
}

typedef std::unordered_set<std::string> Vocabulary;

template<typename Container>
Vocabulary populateVolcabulary(const Container& sentence_list)
{
    Vocabulary result;
    for( const std::string& sentence : sentence_list )
    {
        std::istringstream strm(sentence);
        std::string tmp;
        for( strm >> tmp; strm; strm >> tmp ) // this is roughly equivalent to splitting on spaces
        {
            result.insert(tmp);
        }
    }
    return result;
}

// TODO refactor
// TODO evaluate these hash functions
namespace std {

    template<>
    struct hash<std::tuple<std::string, std::string>>
    {
        std::hash<std::string> str_hash;
        public:
        size_t operator()(const std::tuple<std::string, std::string>& obj) const
        {
            return str_hash(std::get<0>(obj)) ^ str_hash(std::get<1>(obj));
        }
    };

    template<>
    struct hash<std::tuple<unsigned, unsigned>>
    {
        std::hash<unsigned> int_hash;
        public:
        size_t operator()(const std::tuple<unsigned, unsigned>& obj) const
        {
            return int_hash(std::get<0>(obj)) ^ int_hash(std::get<1>(obj));
        }
    };

    template<>
    struct hash<std::tuple<unsigned, unsigned, unsigned, unsigned>>
    {
        std::hash<unsigned> int_hash;
        public:
        size_t operator()(const std::tuple<unsigned, unsigned, unsigned, unsigned>& obj) const
        {
            return int_hash(std::get<0>(obj)) ^ int_hash(std::get<1>(obj))
                ^  int_hash(std::get<2>(obj)) ^ int_hash(std::get<3>(obj));
        }
    };
}



typedef std::unordered_map< std::tuple<std::string, std::string>, double> EmissionParameters;
EmissionParameters initializeEmissionParameters(const Vocabulary& sourceVocab, const Vocabulary& targetVocab)
{
    EmissionParameters params;
    double uniformProbability = 1.0 / targetVocab.size();
    for( const std::string& src : sourceVocab )
    {
        for( const std::string& tgt : targetVocab )
        {
            params.insert(std::make_pair( std::make_tuple(src, tgt), uniformProbability) );
        }
    }
    return params;
}

typedef std::unordered_map<std::tuple<unsigned, unsigned, unsigned, unsigned>, double> AlignmentParameters;
// TODO rename variables
AlignmentParameters initializeAlignmentParameters(
    const std::vector<std::string>& sourceSentenceList,
    const std::vector<std::string>& targetSentenceList
    )
{
    AlignmentParameters alignment_parameters;
    std::unordered_set<std::tuple<unsigned, unsigned>> visited_keys;
    for( unsigned i = 0; i < sourceSentenceList.size() && i < targetSentenceList.size(); ++i )
    {
        const std::string& sourceSentence = sourceSentenceList.at(i);
        const std::string& targetSentence = targetSentenceList.at(i);
        unsigned l = std::count(std::begin(sourceSentence), end(sourceSentence), ' ');
        unsigned m = std::count(std::begin(targetSentence), end(targetSentence), ' ');

        if( visited_keys.find(std::make_tuple(l, m)) != std::end(visited_keys) )
            continue;

        for( unsigned k = 0; k < m; ++k )
        {
            for( unsigned j = 0; j < l; ++j )
            {
                alignment_parameters.insert(make_pair(make_tuple(j, k, l, m), 1.0 / l));
            }
        }

        visited_keys.insert(std::make_tuple(l, m));
    }

    return alignment_parameters;
}

std::vector<std::string> split(const std::string& str, char delim)
{
    std::istringstream strm(str);
    std::vector<std::string> result;
    std::string buff;
    while( std::getline(strm, buff, delim) ) {
        if( buff.size() > 0 )
            result.push_back(buff);
    }
    return result;
}

template<typename T>
static inline T fromString(const std::string& str)
{
    std::istringstream strm(str);
    T val; // can we do this without the default construction?
    strm >> val;
    return val;
}

// TODO this function is really broken
// there are implicit restrictions on type and content of things everywhere
template<typename Container>
double initializeDistanceParameters(const Container& developmentAlignmentsList)
{
    std::unordered_map<std::tuple<std::string, std::string>, unsigned> alignment_count;
    for( const std::string& alignmentLine : developmentAlignmentsList )
    {
        std::istringstream strm(alignmentLine);
        std::string alignment;
        for(strm >> alignment; strm; strm >> alignment) // this is roughly equivalent to splitting on spaces
        {
            std::vector<std::string> alignment_parts;
            if( alignment.size() > 0 && alignment.find('?') != std::string::npos )
                alignment_parts = split(alignment, '?');
            else if( alignment.size() > 0 && alignment.find('-') != std::string::npos )
                alignment_parts = split(alignment, '-');
            else
                throw std::runtime_error("Did not put anything into alignment parts!");
            // Didn't do any bounds checking on alignment parts, so use .at() instead of []
            std::string french_index = alignment_parts.at(0);
            std::string english_index = alignment_parts.at(1);
            // operator[] will default construct a value if it is not already
            // in the set, and the default for unsigned is 0, so this does the right thing(tm)
            alignment_count[make_tuple(french_index, english_index)] += 1;
        }
    }

    // now calculate the distance parameter
    double normalization_constant = std::accumulate(begin(alignment_count), end(alignment_count), 0,
            [](unsigned partial_sum, const std::pair<std::tuple<std::string, std::string>, unsigned> p) {
                return partial_sum + p.second;
            });
    std::vector<int> distance_parameters;
    for( const std::pair<std::tuple<std::string, std::string>, unsigned>& p : alignment_count )
    {
        int distance = abs( fromString<int>(std::get<0>(p.first)) - fromString<int>(std::get<1>(p.first)) );
        if( distance == 0 ) // what's this do?
            distance = 1;
        double probability = static_cast<double>(p.second) / normalization_constant;
        double current_distance_parameter = pow(probability, 1.0 / distance);
        distance_parameters.push_back(current_distance_parameter);
    }

    return std::accumulate(begin(distance_parameters), end(distance_parameters), 0) / distance_parameters.size();
}

struct Parameter
{
    EmissionParameters emit_params;
    AlignmentParameters align_params;
    Parameter(EmissionParameters e, AlignmentParameters a)
        : emit_params(e), align_params(a)
    { }
};

template<typename Container1, typename Container2>
void trainParameters(const Container1& sourceSentenceList, const Container2& targetSentenceList,
        unsigned targetVocabSize,
        EmissionParameters& emission_params, AlignmentParameters& align_params,
        unsigned numIterations, int modelNo
    )
{
    for( unsigned iterations = 0; iterations < numIterations; ++iterations )
    {
        std::unordered_map<int, int> emission_counts;
        std::unordered_map<int, int> alignment_conts;
        std::unordered_set<std::tuple<std::string, std::string>> modified_emission_keys;
        std::unordered_set<std::tuple<unsigned, unsigned, unsigned, unsigned>> modified_alignment_keys;

        for( unsigned current_training_idx = 0; current_training_idx < sourceSentenceList.size(); ++current_training_idx )
        {
            std::vector<std::string> current_source_word_list = split(sourceSentenceList[current_training_idx], ' ');
            std::vector<std::string> current_target_word_list = split(targetSentenceList[current_training_idx], ' ');
            unsigned l = current_source_word_list.size();
            unsigned m = current_target_word_list.size();

            for( unsigned i = 0; i < current_target_word_list.size(); ++i )
            {
                std::string target_word = current_target_word_list[i];
                double denominator = 0;

                if( modelNo == 1 ) // TODO refactor
                {
                    for( const std::string& w : current_source_word_list )
                    {
                        auto tuple_key = make_tuple(w, target_word);
                        EmissionParameters::iterator location = emission_params.find(tuple_key);
                        if( location != end(emission_params) )
                            denominator += location->second;
                        else {
                            denominator += 1.0 / targetVocabSize;
                            emission_params.insert(make_pair(tuple_key, 1.0 / targetVocabSize));
                        }
                    }
                }
                else if( modelNo == 2 )
                {
                    for( unsigned count = 0; count < l; ++count )
                    {
                        auto tuple_key = make_tuple(count, i, l, m);
                        AlignmentParameters::iterator location = align_params.find(tuple_key);
                        double prob = 0;
                        if( location == end(align_params) ) {
                            prob = 1.0 / static_cast<double>(l);
                            align_params.insert(make_pair(tuple_key, prob));
                        }
                        else {
                            prob = location->second;
                        }
                        denominator +=
                               prob * emission_params[make_tuple(current_source_word_list[count], target_word)];
                    }
                }

                for( unsigned j = 0; j < current_source_word_list.size(); ++j )
                {
                    const std::string& source_word = current_source_word_list[j];

                    auto emission_key = make_tuple(source_word, target_word);
                    auto align_key = make_tuple(j, i, l, m);

                    modified_emission_keys.insert(emission_key);
                    modified_alignment_keys.insert(align_key);

                    double delta = emission_params[emission_key];
                    if( modelNo == 2 )
                        delta *= align_params[align_key];
                    delta /= denominator;

                    // The corresponding python (lines 200-227)
                    // is not correct, so I have not transliterated it
                }
            }
        }
    }
}

template<typename Container1, typename Container2>
void makeAndPrintPredictions(const Container1& sourceSentenceList, const Container2& targetSentenceList,
        const EmissionParameters& emissionParams, const AlignmentParameters& alignmentParams,
        double distanceParameter
    )
{
    for( unsigned current_idx = 0; current_idx < 1000; ++current_idx )
    {
        std::vector<std::string> current_source_word_list = split(sourceSentenceList[current_idx], ' ');
        std::vector<std::string> current_target_word_list = split(targetSentenceList[current_idx], ' ');
        unsigned l = current_source_word_list.size();
        unsigned m = current_target_word_list.size();

        std::ostringstream alignmentString;
        for(unsigned i = 0; i < current_target_word_list.size(); ++i )
        {
            const std::string& target_word = current_target_word_list[i];
            alignmentString << i;

            unsigned current_max_index = 0;
            double current_max;

            for( unsigned j = 0; j < current_source_word_list.size(); ++j)
            {
                const std::string& source_word = current_source_word_list[j];
                double current_val =
                      emissionParams.at(make_tuple(source_word, target_word))
                    * alignmentParams.at(make_tuple(j,i,l,m))
                    * pow(distanceParameter, abs(i-j));
                if( current_max < current_val )
                {
                    current_max = current_val;
                    current_max_index = j;
                }
            }
            std::cout << alignmentString.str() << "\n";
        }
    }
}

int main()
{
    std::vector<std::string> englishSentenceList = readFile("data/hansards.e", 9999);
    std::vector<std::string> frenchSentenceList = readFile("data/hansards.f", 9999);
    std::vector<std::string> developmentAlignmentsList = readFile("data/hansards.a", 37);

    // compute the french vocabulary
    std::unordered_set<std::string> frenchVocabulary = populateVolcabulary(frenchSentenceList);

    // get the initial parameters
    double distanceParameter = initializeDistanceParameters(developmentAlignmentsList);

    // Create the parameters for training
    EmissionParameters emission_parameters;
    AlignmentParameters alignment_parameters;

    // train for model 1
    trainParameters(englishSentenceList, frenchSentenceList, frenchVocabulary.size(), emission_parameters, alignment_parameters, 10, 1);

    // train for model 2
    trainParameters(englishSentenceList, frenchSentenceList, frenchVocabulary.size(), emission_parameters, alignment_parameters, 10, 2);

    // Write the predictions out
    makeAndPrintPredictions(englishSentenceList, frenchSentenceList, emission_parameters, alignment_parameters, distanceParameter);

    return 0;
}
