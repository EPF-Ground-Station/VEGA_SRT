#ifndef ERROR_H
#define ERROR_H

#include <string>

enum class ErrorType { NONE, WARNING, ERROR };

struct ErrorStatus {

    ErrorType type;
    std::string msg;

    ErrorStatus()
    {
        type = ErrorType::NONE;
        msg = "";
    }

    ErrorStatus(ErrorType type, std::string msg) : 
        type(type),
        msg(msg)
        {}


};

#endif