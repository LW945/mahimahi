/* -*-mode:c++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */

#ifndef CELL_QUEUE_HH
#define CELL_QUEUE_HH

#include <queue>
#include <cstdint>
#include <string>

#include "file_descriptor.hh"

class CellQueue
{
private:
    uint64_t delay_ms_;
    std::queue< std::pair<uint64_t, std::string> > packet_queue_;
    /* release timestamp, contents */

public:
    CellQueue( const uint64_t & s_delay_ms ) : delay_ms_( s_delay_ms ), packet_queue_() {}

    void read_packet( const std::string & contents );

    void write_packets( FileDescriptor & fd );

    int wait_time( void ) const;
};

#endif /* CELL_QUEUE_HH */